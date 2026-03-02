import pytest
import os
from cmm18c.master import load_master_csv

@pytest.fixture(scope="session")
def master_fixture():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "MH-28-v1.0-18D.csv")
    if not os.path.exists(csv_path):
        # Fallback to absolute if relatives fail in some test envs
        csv_path = "c:/hijaiyyah-codex/cmm18c/data/MH-28-v1.0-18D.csv"
    return load_master_csv(csv_path)
