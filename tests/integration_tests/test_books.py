from httpx import AsyncClient
import uuid
from src.security import hash_password
from src.utilis.enums import RoleEnum


async def test_books_crud(ac: AsyncClient, db):
    await ac.post("/auth/register", json={
        "username": "booker",
        "email": "booker@example.com",
        "password": "secret123"
    })
    token_resp = await ac.post(
        "/auth/token",
        data={"username": "booker", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_user = token_resp.json()["access_token"]
    headers_user = {"Authorization": f"Bearer {token_user}"}

    resp = await ac.post("/authors/", json={"bio": "Book author", "profile_picture": None}, headers=headers_user)
    assert resp.status_code == 201
    author_id = resp.json()["id"]

    admin = await db.users.create({
        "id": uuid.uuid4(),
        "username": "admin2",
        "email": "admin@example2.com",
        "hashed_password": hash_password("adminpass"),
        "role": RoleEnum.ADMIN,
        "is_active": True,
    })

    token_resp = await ac.post(
        "/auth/token",
        data={"username": "admin2", "password": "adminpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_admin = token_resp.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    resp = await ac.post("/genres", json={"name": "Test Genre"}, headers=headers_admin)
    assert resp.status_code == 201
    genre_id = resp.json()["id"]

    resp = await ac.post("/books/", json={
        "title": "The Test Book",
        "description": "A test book description",
        "file_path": "uploads/test.pdf",
        "author_id": author_id,
        "genre_ids": [genre_id]
    }, headers=headers_user)
    assert resp.status_code == 201
    book = resp.json()
    assert book["title"] == "The Test Book"
    book_id = book["id"]

    resp = await ac.get(f"/books/{book_id}", headers=headers_user)
    assert resp.status_code == 200
    assert resp.json()["id"] == book_id

    resp = await ac.put(f"/books/{book_id}", json={
        "title": "Updated Book",
        "description": "Updated desc",
        "file_path": "uploads/updated.pdf",
        "genre_ids": [genre_id]
    }, headers=headers_user)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Book"

    resp = await ac.delete(f"/books/{book_id}", headers=headers_user)
    assert resp.status_code == 204

