import pytest
from io import BytesIO

class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test that root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Procon Ágil" in response.json()["message"]


class TestChatEndpoint:
    def test_chat_returns_response(self, client, sample_chat_message):
        """Test that chat endpoint returns a valid response."""
        response = client.post("/api/chat", json=sample_chat_message)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"]["role"] == "assistant"
        assert len(data["message"]["content"]) > 0

    def test_chat_with_maintenance_keyword(self, client):
        """Test that maintenance-related messages get legal analysis."""
        payload = {"messages": [{"role": "user", "content": "infiltração no teto"}]}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        # Should be a meaningful response (not empty)
        content = response.json()["message"]["content"]
        assert len(content) > 20
        assert response.json()["message"]["role"] == "assistant"


class TestUploadEndpoint:
    def test_upload_valid_image(self, client):
        """Test uploading a valid image file."""
        # Create a fake JPG file
        fake_image = BytesIO(b'\xFF\xD8\xFF' + b'\x00' * 100)  # Basic JPEG header
        files = {"file": ("test.jpg", fake_image, "image/jpeg")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "forensic_analysis" in data

    def test_upload_invalid_type(self, client):
        """Test that invalid file types are rejected."""
        fake_exe = BytesIO(b'\x00' * 100)
        files = {"file": ("malware.exe", fake_exe, "application/x-msdownload")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert "não suportado" in response.json()["detail"]


class TestClaimEndpoint:
    def test_generate_claim(self, client, sample_claim_data):
        """Test that claim generation returns structured document."""
        response = client.post("/api/claim/generate", json=sample_claim_data)
        assert response.status_code == 200
        data = response.json()
        # Generator may return raw or processed format depending on input
        assert "title" in data or "analysis" in data or "facts" in data


class TestAutomationEndpoint:
    def test_submit_claim_mock(self, client):
        """Test that automation submission works (mocked)."""
        payload = {
            "claim_data": {
                "title": "Teste",
                "facts": "Fatos de teste",
                "request": "Pedido de teste",
                "value": "R$ 1.000"
            }
        }
        response = client.post("/api/automation/submit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "protocol" in data
        assert len(data["logs"]) > 0
