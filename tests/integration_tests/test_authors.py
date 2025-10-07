from httpx import AsyncClient


async def test_create_update_delete_author(ac: AsyncClient):
    await ac.post("/auth/register", json={
        "username": "author1",
        "email": "author1@example.com",
        "password": "secret123"
    })
    token_resp = await ac.post(
        "/auth/token",
        data={"username": "author1", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await ac.post("/authors/", json={"bio": "Writer bio", "profile_picture": None}, headers=headers)
    assert resp.status_code == 201
    author = resp.json()
    assert author["bio"] == "Writer bio"
    author_id = author["id"]

    resp = await ac.put(f"/authors/{author_id}", json={"bio": "Updated bio", "profile_picture": None}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Updated bio"

    resp = await ac.delete(f"/authors/{author_id}", headers=headers)
    assert resp.status_code == 204
