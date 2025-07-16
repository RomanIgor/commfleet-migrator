import streamlit as st
import json
import hashlib
from pathlib import Path

USER_FILE = Path("users.json")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not USER_FILE.exists():
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_admins_from_secrets():
    return st.secrets.get("admin_users", {})

def validate_user(username, password):
    password_hash = hash_password(password)

    # Prioritate: admini din secrets.toml
    admin_users = load_admins_from_secrets()
    if username in admin_users and admin_users[username] == password_hash:
        return True

    # Altfel, caută în users.json
    users = load_users()
    if username in users:
        return users[username]["password"] == password_hash

    return False

def get_user_role(username):
    # Admini din secrets au întotdeauna rolul "admin"
    if username in load_admins_from_secrets():
        return "admin"
    users = load_users()
    return users.get(username, {}).get("role", "user")

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def add_user(username, password, role="user"):
    users = load_users()
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    save_users(users)
