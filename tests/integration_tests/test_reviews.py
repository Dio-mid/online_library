from httpx import AsyncClient


async def test_reviews_crud(ac: AsyncClient):
    await ac.post("/auth/register", json={
        "username": "reviewer",
        "email": "reviewer@example.com",
        "password": "secret123"
    })
    token_resp = await ac.post(
        "/auth/token",
        data={"username": "reviewer", "password": "secret123"},
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

    resp = await ac.post("/reviews/", json={
        "book_id": book_id,
        "rating": 5,
        "text": "Amazing book!"
    }, headers=headers)
    assert resp.status_code == 201
    review = resp.json()
    assert review["rating"] == 5

    resp = await ac.put(f"/reviews/{book_id}", json={
        "rating": 4,
        "text": "Good, but not perfect"
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["rating"] == 4

    resp = await ac.delete(f"/reviews/{book_id}", headers=headers)
    assert resp.status_code == 204
