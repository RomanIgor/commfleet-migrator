import streamlit as st
import pandas as pd
from difflib import get_close_matches
from datetime import datetime
import io
import json
from pathlib import Path
import traceback

from utils.auth import validate_user, get_user_role  # 🔐 Login-Funktionen
import os

# Templates laden mit Fehlerbehandlung
def load_templates():
    try:
        with open('templates.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'templates' not in data:
                st.error("Ungültiges Format: Schlüssel 'templates' fehlt")
                return {}
            return data['templates']
    except FileNotFoundError:
        st.error("templates.json wurde nicht gefunden")
        return {}
    except json.JSONDecodeError:
        st.error("Ungültiges JSON-Format in templates.json")
        return {}
    except Exception as e:
        st.error(f"Fehler beim Laden der Templates: {str(e)}")
        return {}

# Login-Formular anzeigen
def login_form():
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Benutzername oder Passwort ist falsch")

# Hauptfunktion der Anwendung
def main():
    st.set_page_config(
        page_title="Commfleet Data Migrator Pro",
        layout="wide",
        page_icon="🚗"
    )

    # Login-Zustand verwalten
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_form()
        return

    # Sidebar Navigation
    st.sidebar.success(f"👋 Willkommen, {st.session_state.username}!")
    is_admin = get_user_role(st.session_state.username) == "admin"
    page = st.sidebar.radio(
        "Navigation",
        ["Migration", "Benutzerverwaltung"] if is_admin else ["Migration"]
    )

    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # Datenmigration starten
    st.title("🔁 Commfleet Data Migrator")

    TEMPLATES = load_templates()
    if not TEMPLATES:
        st.stop()

    with st.sidebar:
        st.image("logo.png", width=200) if Path("logo.png").exists() else st.write("Logo")
        selected_template = st.selectbox(
            "Template auswählen",
            options=list(TEMPLATES.keys()),
            format_func=lambda x: f"{x} - {TEMPLATES[x].get('description', '')}"
        )
        st.markdown("---")
        st.markdown(f"**Pflichtfelder:**\n- " + "\n- ".join(TEMPLATES[selected_template]['required']))

    uploaded_file = st.file_uploader("Kundendatei hochladen", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            process_migration(uploaded_file, TEMPLATES[selected_template], selected_template)
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {str(e)}")
            st.text(traceback.format_exc())

# Migrationsverarbeitung bleibt unverändert
def process_migration(uploaded_file, template_config, template_name):
    try:
        template_path = template_config['file']
        if not Path(template_path).exists():
            raise FileNotFoundError(f"Template-Datei nicht gefunden: {template_path}")

        template = pd.read_excel(template_path)

        if uploaded_file.name.endswith('.xlsx'):
            client_data = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            client_data = pd.read_csv(uploaded_file)
        else:
            raise ValueError("Dateiformat wird nicht unterstützt")

        if client_data.empty:
            raise ValueError("Die hochgeladene Datei ist leer")

    except Exception as e:
        st.error(f"Fehler beim Laden der Dateien: {str(e)}")
        return

    # Automatisches Mapping
    st.subheader("📊 Spaltenzuordnung")
    mapping = {}
    stats = {
        'exact_matches': 0,
        'fuzzy_matches': 0,
        'no_matches': 0,
        'warnings': []
    }

    for client_col in client_data.columns:
        try:
            exact_match = [t_col for t_col in template.columns
                           if str(client_col).strip().lower() == str(t_col).strip().lower()]

            if exact_match:
                mapping[client_col] = exact_match[0]
                stats['exact_matches'] += 1
            else:
                matches = get_close_matches(
                    str(client_col).strip(),
                    [str(col).strip() for col in template.columns],
                    n=1,
                    cutoff=0.6
                )
                if matches:
                    mapping[client_col] = matches[0]
                    stats['fuzzy_matches'] += 1
                    stats['warnings'].append(f"Fuzzy-Match: {client_col} → {matches[0]}")
                else:
                    mapping[client_col] = None
                    stats['no_matches'] += 1
        except Exception as e:
            stats['warnings'].append(f"Fehler beim Mapping {client_col}: {str(e)}")
            mapping[client_col] = None

    # Statistik anzeigen
    cols = st.columns(3)
    cols[0].metric("Exakte Übereinstimmungen", stats['exact_matches'])
    cols[1].metric("Fuzzy Matches", stats['fuzzy_matches'])
    cols[2].metric("Nicht zugeordnet", stats['no_matches'])

    # Manuelle Anpassung
    with st.expander("🔧 Zuordnung anpassen", expanded=True):
        for client_col, template_col in mapping.items():
            options = ["-- Nicht zugeordnet --"] + list(template.columns)
            current_index = options.index(template_col) if template_col in options else 0
            new_mapping = st.selectbox(
                f"**{client_col}** →",
                options,
                index=current_index,
                key=f"map_{client_col}"
            )
            mapping[client_col] = new_mapping if new_mapping != "-- Nicht zugeordnet --" else None

    # Pflichtfelder überprüfen
    st.subheader("🔍 Validierung")
    missing_fields = [f for f in template_config['required'] if f not in mapping.values()]
    if missing_fields:
        st.error(f"❌ Fehlende Pflichtfelder: {', '.join(missing_fields)}")
    else:
        st.success("✅ Alle Pflichtfelder sind zugeordnet")

    if stats['warnings']:
        with st.expander("⚠️ Warnungen"):
            for warning in stats['warnings']:
                st.warning(warning)

    # Daten transformieren
    result = pd.DataFrame(columns=template.columns)
    unmapped_data = pd.DataFrame()

    for client_col, template_col in mapping.items():
        if template_col:
            result[template_col] = client_data[client_col]
        else:
            unmapped_data[client_col] = client_data[client_col]

    # Vorschau
    st.subheader("👀 Vorschau")
    tab1, tab2, tab3 = st.tabs(["Mapping-Daten", "Originaldaten", "Nicht zugeordnet"])

    with tab1:
        st.dataframe(result.head(), use_container_width=True)
        st.markdown(f"**Zeilen:** {len(result)} | **Spalten:** {len(result.columns)}")

    with tab2:
        st.dataframe(client_data.head(), use_container_width=True)
        st.markdown(f"**Zeilen:** {len(client_data)} | **Spalten:** {len(client_data.columns)}")

    with tab3:
        if not unmapped_data.empty:
            st.dataframe(unmapped_data.head(), use_container_width=True)
            st.markdown(f"**Nicht zugeordnete Spalten:** {len(unmapped_data.columns)}")
        else:
            st.info("Alle Spalten wurden erfolgreich zugeordnet")

    # Export
    st.subheader("📤 Export")
    output = io.BytesIO()

    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result.to_excel(writer, sheet_name="Mapped_Data", index=False)

            metadata = {
                "Migration": {
                    "Datum": datetime.now().strftime('%Y-%m-%d %H:%M'),
                    "Template": template_name,
                    "Dateiname": uploaded_file.name,
                    "Trefferquote": f"{len(result.columns)}/{len(client_data.columns)}"
                },
                "Statistik": stats
            }

            pd.DataFrame.from_dict(metadata, orient='index').to_excel(writer, sheet_name="Metadata")

            mapping_df = pd.DataFrame({
                "Quellspalte": mapping.keys(),
                "Zielspalte": [v if v else "-- Nicht zugeordnet --" for v in mapping.values()],
                "Status": ["Zugeordnet" if v else "Nicht zugeordnet" for v in mapping.values()]
            })
            mapping_df.to_excel(writer, sheet_name="Mapping", index=False)

            if not unmapped_data.empty:
                unmapped_data.to_excel(writer, sheet_name="Nicht_zugeordnet", index=False)

        output.seek(0)

        st.download_button(
            label="📁 Gesamten Bericht herunterladen",
            data=output,
            file_name=f"migration_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Fehler beim Export: {str(e)}")

# Startpunkt
if __name__ == "__main__":
    main()

