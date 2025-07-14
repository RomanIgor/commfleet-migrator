# 🔐 Authentifizierungsmodul für Streamlit-App
import json
import hashlib
from pathlib import Path

# Pfad zur Benutzerdatei
USER_FILE = Path("users.json")

# Passwort hashen mit SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Benutzer aus Datei laden
def load_users():
    if not USER_FILE.exists():
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Benutzer in Datei speichern
def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# Benutzername und Passwort validieren
def validate_user(username, password):
    users = load_users()
    if username in users:
        return users[username]["password"] == hash_password(password)
    return False

# Neuen Benutzer hinzufügen (z. B. durch Admin)
def add_user(username, password, role="user"):
    users = load_users()
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    save_users(users)

# Rolle eines Benutzers abrufen (z. B. admin oder user)
def get_user_role(username):
    users = load_users()
    return users.get(username, {}).get("role", "user")
