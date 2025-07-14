import pytest
from pathlib import Path
import shutil

from utils.create_admin_user import load_templates

TEMPLATE_FILE = Path("templates.json")
TEMPLATE_BACKUP = Path("templates_backup.json")

@pytest.fixture(scope="module", autouse=True)
def restore_templates():
    if TEMPLATE_FILE.exists():
        shutil.copy(TEMPLATE_FILE, TEMPLATE_BACKUP)
    yield
    if TEMPLATE_BACKUP.exists():
        shutil.copy(TEMPLATE_BACKUP, TEMPLATE_FILE)

def test_load_templates_success():
    templates = load_templates()
    assert isinstance(templates, dict)
    assert len(templates) > 0

def test_load_templates_missing():
    TEMPLATE_FILE.rename("templates_temp.json")
    try:
        result = load_templates()
        assert result == {}
    finally:
        Path("templates_temp.json").rename(TEMPLATE_FILE)
