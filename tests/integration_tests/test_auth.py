from httpx import AsyncClient


async def test_register_and_login(ac: AsyncClient):
    resp = await ac.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"

    resp = await ac.post(
        "/auth/token",
        data={"username": "testuser", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
