"""
Integration tests for FastAPI endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert data["product_name"] == "CareerMatch AI"
        assert data["zero_keyword_matching_guarantee"] is True


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register
        reg_payload = {
            "email": "student_test@careermatch.ai",
            "password": "securepassword123",
            "full_name": "Test Candidate",
            "target_role": "Machine Learning Engineer",
            "experience_level": "Fresher"
        }
        reg_res = await ac.post("/api/auth/register", json=reg_payload)
        # 200 or 400 if already exists
        assert reg_res.status_code in [200, 400]

        # Login
        login_res = await ac.post("/api/auth/login", json={
            "email": reg_payload["email"],
            "password": reg_payload["password"]
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        # Profile / Me with token
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await ac.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == reg_payload["email"]
