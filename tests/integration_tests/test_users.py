from httpx import AsyncClient
import uuid
from src.security import hash_password
from src.utilis.enums import RoleEnum

async def test_users_crud(ac: AsyncClient, db):
    await ac.post("/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "secret123"
    })
    token_resp = await ac.post(
        "/auth/token",
        data={"username": "user1", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_user = token_resp.json()["access_token"]
    headers_user = {"Authorization": f"Bearer {token_user}"}

    admin = await db.users.create({
        "id": uuid.uuid4(),
        "username": "admin3",
        "email": "admin@example3.com",
        "hashed_password": hash_password("adminpass"),
        "role": RoleEnum.ADMIN,
        "is_active": True,
    })
    token_resp = await ac.post(
        "/auth/token",
        data={"username": "admin3", "password": "adminpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_admin = token_resp.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    resp = await ac.get("/users", headers=headers_admin)
    assert resp.status_code == 200
    users = resp.json()
    assert any(user["username"] == "user1" for user in users)

    user_id = [user for user in users if user["username"]=="user1"][0]["id"]
    resp = await ac.get(f"/users/{user_id}", headers=headers_user)
    assert resp.status_code == 200
    assert resp.json()["username"] == "user1"

    resp = await ac.patch("/users/me", json={"username": "user1_updated"}, headers=headers_user)
    assert resp.status_code == 200
    assert resp.json()["username"] == "user1_updated"

    resp = await ac.patch(f"/users/{user_id}", json={"username": "user1_by_admin"}, headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json()["username"] == "user1_by_admin"

    resp = await ac.delete(f"/users/{user_id}", headers=headers_admin)
    assert resp.status_code == 204

    resp = await ac.get(f"/users/{user_id}", headers=headers_admin)
    assert resp.status_code == 404
