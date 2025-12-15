import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)

@pytest.fixture
def sample_chat_message():
    """Sample chat request payload."""
    return {
        "messages": [
            {"role": "user", "content": "Tenho um problema de infiltração no apartamento"}
        ]
    }

@pytest.fixture
def sample_claim_data():
    """Sample claim generation payload."""
    return {
        "report": "A torneira vazou e causou mofo na parede",
        "forensic_data": {},
        "legal_analysis": {}
    }
