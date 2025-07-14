import pytest
from utils.auth import validate_user, add_user
import json
from pathlib import Path

USERS_FILE = Path("users.json")

@pytest.fixture(scope="module")
def setup_test_user():
    username = "testuser"
    password = "testpass"
    # Backup users.json
    original = USERS_FILE.read_text(encoding="utf-8")
    add_user(username, password, role="user")
    yield username, password
    # Restore original
    USERS_FILE.write_text(original, encoding="utf-8")

def test_validate_user_success(setup_test_user):
    username, password = setup_test_user
    assert validate_user(username, password) == True

def test_validate_user_fail():
    assert validate_user("wronguser", "wrongpass") == False
