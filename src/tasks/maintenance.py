import asyncio

from src.database import async_session_maker_null_pool
from src.utilis.celery_app import celery_app
from src.utilis.redis_manager import RedisManager
from src.config import settings


@celery_app.task
def refresh_materialized_views():
    print("[Celery] Refreshing materialized views...")

    async def _refresh():
        async with async_session_maker_null_pool() as session:
            try:
                await session.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY book_stats;")
                await session.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY top_authors;")
                await session.commit()
                print("[Celery] Materialized views refreshed successfully")
            except Exception as exc:
                await session.rollback()
                print(f"[Celery] Error refreshing materialized views: {exc}")

    asyncio.run(_refresh())


@celery_app.task
def cleanup_redis_cache():

    async def _cleanup():
        print("[Celery] Starting Redis cache cleanup...")
        redis = RedisManager(settings.REDIS_HOST, settings.REDIS_PORT)
        await redis.connect()

        deleted_books = await redis.delete("search:books:*")
        deleted_tmp = await redis.delete("tmp:*")

        await redis.close()
        print(f"[Celery] Redis cleanup done. Deleted: search={deleted_books}, tmp={deleted_tmp}")

    asyncio.run(_cleanup())
