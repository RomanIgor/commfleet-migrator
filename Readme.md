# Commfleet Data Migrator 

Ein leichtgewichtiges, hilfreiches Webtool zur Unterstützung bei der Migration von Fahrzeuge, G_Partners usw. aus Excel/CSV-Dateien in das Commfleet-System.

---

## 🔍 Zweck der Anwendung

In der ersten Phase eines neuen Kundenprojekts müssen bestehende Daten – häufig in eigenen Excel-Dateien gepflegt – in strukturierte Templates überführt werden, um sie in Commfleet zu importieren. 

Dieses Tool unterstützt genau diesen ersten Schritt: Es bietet eine Möglichkeit, die Übertragung von bestehenden Excel-Daten in unsere Templates zu erleichtern und teilweise zu automatisieren.

Funktionen:

- Auswahl eines Templates mit Pflichtfeldern
- Automatische Spaltenzuordnung (auch bei unterschiedlichen Bezeichnungen)
- Möglichkeit zur manuellen Korrektur der Zuordnung
- Vorschau und Validierung der Daten
- Export eines strukturierten Migrationsberichts
- Benutzerverwaltung ohne Datenbank

---

## 🚀 Lokale Installation

### Voraussetzungen
- Python 3.9 oder höher
- `pip`

### Installation
```bash
# Repository klonen oder Code herunterladen
cd commfleet-migrator

# Virtuelle Umgebung (empfohlen)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Anwendung starten
```bash
streamlit run main.py
```

---

## 🧪 Tests ausführen
```bash
python -m pytest tests/
```
Tests prüfen z. B. Benutzeranmeldung und Template-Logik.

---

## 🌐 Deployment (optional via Streamlit Cloud)

1. GitHub-Repository erstellen (z. B. `commfleet-migrator`)
2. Code hochladen (inkl. `requirements.txt` und `.streamlit/config.toml`)
3. Gehe zu [https://streamlit.io/cloud](https://streamlit.io/cloud)
4. Repository und Datei `main.py` wählen
5. Deploy klicken

Danach ist die App erreichbar unter z. B.:
```
https://dein-nutzername-commfleet-migrator.streamlit.app
```

---

## 🔐 Standard-Login

| Benutzername | Passwort | Rolle  |
|--------------|----------|--------|
| admin        | admin    | admin  |

Benutzer werden lokal in der Datei `users.json` gespeichert. 
Die Benutzerverwaltung kann über das Seitenmenü aufgerufen werden.

---

## 🗂️ Projektstruktur
```text
commfleet-migrator/
├── main.py                  # Hauptlogik & Login
├── pages/
│   └── admin_user_manager.py
├── utils/
│   └── auth.py
├── templates.json          # Definition der Template-Felder
├── users.json              # Benutzerverwaltung (lokal)
├── requirements.txt        # Abhängigkeiten
├── .streamlit/
│   └── config.toml         # Design-Konfiguration
├── tests/                  # Unittests
│   ├── test_auth.py
│   └── test_templates.py
├── logo.png (optional)
└── README.md
```

---

## 📩 Feedback & Weiterentwicklung

Die Lösung ist bewusst einfach gehalten, modular aufgebaut und kann je nach Projektanforderung erweitert werden – z. B. mit mehreren Templates, rollenbasiertem Zugriff oder zusätzlicher Validierungslogik.

Rückfragen und Anregungen bitte direkt an das Entwicklerteam.
