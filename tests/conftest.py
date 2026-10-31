import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def sortify_home(tmp_path_factory, monkeypatch):
    """Keep logs and trash of every test away from the real ~/.sortify."""
    home = tmp_path_factory.mktemp("sortify_home")
    monkeypatch.setenv("SORTIFY_HOME", str(home))
    return home
