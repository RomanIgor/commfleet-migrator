# 🔐 Admin-Oberfläche zum Hinzufügen neuer Benutzer
import streamlit as st
from utils.auth import add_user, load_users, get_user_role

# Nur für Admins zugänglich
def admin_panel():
    st.title("👥 Benutzerverwaltung")

    # Aktuelle Benutzer anzeigen
    users = load_users()
    st.subheader("📋 Bestehende Benutzer")
    st.table([{"Benutzername": k, "Rolle": v["role"]} for k, v in users.items()])

    st.markdown("---")
    st.subheader("➕ Neuen Benutzer hinzufügen")

    with st.form("add_user_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        role = st.selectbox("Rolle", ["user", "admin"])
        submit = st.form_submit_button("Benutzer erstellen")

        if submit:
            if username in users:
                st.warning("Benutzername existiert bereits")
            elif len(username) < 3 or len(password) < 4:
                st.error("Benutzername oder Passwort zu kurz")
            else:
                add_user(username, password, role)
                st.success(f"Benutzer '{username}' wurde erfolgreich hinzugefügt")
                st.rerun()

# Zugriffssteuerung prüfen
def main():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("Nicht autorisiert. Bitte zuerst einloggen.")
        return

    if get_user_role(st.session_state.username) != "admin":
        st.error("Nur Admins haben Zugriff auf dieses Panel.")
        return

    admin_panel()

if __name__ == "__main__":
    main()
