from httpx import AsyncClient


async def test_crud_favourite(ac: AsyncClient):
    await ac.post("/auth/register", json={
        "username": "favuser",
        "email": "favuser@example.com",
        "password": "secret123"
    })
    token_resp = await ac.post(
        "/auth/token",
        data={"username": "favuser", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await ac.post("/authors/", json={"bio": "Reviews author", "profile_picture": None}, headers=headers)
    assert resp.status_code == 201
    author_id = resp.json()["id"]

    resp = await ac.post("/books/", json={
        "title": "The Test Book",
        "description": "A test book description",
        "file_path": "uploads/test.pdf",
        "author_id": author_id,
        "genre_ids": []
    }, headers=headers)
    book_id = resp.json()["id"]

    resp = await ac.post("/favourites", json={"book_id": book_id}, headers=headers)
    assert resp.status_code == 201
    fav = resp.json()
    assert fav["book_id"] == book_id

    resp = await ac.get("/favourites", headers=headers)
    assert resp.status_code == 200
    favourites = resp.json()
    assert any(f["book_id"] == book_id for f in favourites)

    resp = await ac.delete(f"/favourites/{book_id}", headers=headers)
    assert resp.status_code == 204
