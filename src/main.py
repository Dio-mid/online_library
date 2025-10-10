import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
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

from src.init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_authors)
app.include_router(router_books)
app.include_router(router_genres)
app.include_router(router_reviews)
app.include_router(router_favourites)


if __name__ == "__main__":
    uvicorn.run("main:app")
