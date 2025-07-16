import pytest
import json
from pathlib import Path
import streamlit as st
from utils.auth import validate_user, add_user

USERS_FILE = Path("users.json")

@pytest.fixture(scope="module")
def setup_test_user():
    username = "testuser"
    password = "testpass"
    # Backup users.json
    original = USERS_FILE.read_text(encoding="utf-8") if USERS_FILE.exists() else "{}"
    add_user(username, password, role="user")
    yield username, password
    # Restore original
    USERS_FILE.write_text(original, encoding="utf-8")

def test_validate_user_success(setup_test_user):
    username, password = setup_test_user
    assert validate_user(username, password) == True

def test_validate_user_fail():
    assert validate_user("wronguser", "wrongpass") == False

def test_admin_from_secrets(monkeypatch):
    # Mock st.secrets
    fake_secrets = {
        "admin_users": {
            "admin": "e51c6f420410b0ed7470756db353c17c128ef4e3d6a03267429f144fbcf9de0a"
        }
    }
    monkeypatch.setattr(st, "secrets", fake_secrets)
    assert validate_user("admin", "fleet") == True
    assert validate_user("admin", "wrongpass") == False
