from httpx import AsyncClient
import uuid
from src.security import hash_password
from src.utilis.enums import RoleEnum


async def test_genres_crud_as_admin(ac: AsyncClient, db):
    admin = await db.users.create({
        "id": uuid.uuid4(),
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": hash_password("adminpass"),
        "role": RoleEnum.ADMIN,
        "is_active": True,
    })

    token_resp = await ac.post(
        "/auth/token",
        data={"username": "admin", "password": "adminpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await ac.post("/genres", json={"name": "Fantasy"}, headers=headers)
    assert resp.status_code == 201
    genre = resp.json()
    assert genre["name"] == "Fantasy"
    genre_id = genre["id"]

    resp = await ac.put(f"/genres/{genre_id}", json={"name": "Epic Fantasy"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Epic Fantasy"

    resp = await ac.delete(f"/genres/{genre_id}", headers=headers)
    assert resp.status_code == 204
