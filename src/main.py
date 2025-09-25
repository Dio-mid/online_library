import sys
from pathlib import Path

from fastapi import FastAPI
import uvicorn

sys.path.append(
    str(Path(__file__).parent.parent)
)

from src.api.auth import router as router_auth
from src.api.users import router as router_users
from src.api.authors import router as router_authors
from src.api.books import router as router_books
from src.api.genres import router as router_genres
from src.api.reviews import router as router_reviews
from src.api.favourites import router as router_favourites

app = FastAPI()

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_authors)
app.include_router(router_books)
app.include_router(router_genres)
app.include_router(router_reviews)
app.include_router(router_favourites)


if __name__ == "__main__":
    uvicorn.run("main:app")
