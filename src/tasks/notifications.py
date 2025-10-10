import asyncio
from email.message import EmailMessage

from aiosmtplib import SMTP
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import async_session_maker_null_pool
from src.models import BooksOrm, AuthorsOrm
from src.utilis.celery_app import celery_app
from src.config import settings
from src.utilis.db_manager import DBManager


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_notification_to_author(self, book_id: str, user_id: str):

    async def _send():
        async with DBManager(session_factory=async_session_maker_null_pool) as db:
            review = await db.reviews.get_one(book_id=book_id, user_id=user_id)
            if not review:
                print(f"[Celery] Review not found for book={book_id}, user={user_id}")
                return

            stmt = (
                select(BooksOrm)
                .options(
                    selectinload(BooksOrm.author)
                    .selectinload(AuthorsOrm.user)
                )
                .where(BooksOrm.id == book_id)
            )
            result = await db.session.execute(stmt)
            book = result.scalar_one_or_none()

            if not book or not book.author or not book.author.user:
                print(f"[Celery] Author or user not found for book={book_id}")
                return

            author = book.author
            author_email = author.user.email
            author_name = getattr(author.user, "username", "Автор")

            subject = f"Новый отзыв на вашу книгу «{book.title}»"
            body = (
                f"Здравствуйте, {author_name}!\n\n"
                f"На вашу книгу «{book.title}» оставлен новый отзыв.\n\n"
                f"Рейтинг: {review.rating}/5\n"
                f"Комментарий: {review.text}\n\n"
                f"С уважением,\nКоманда Online Library"
            )

            message = EmailMessage()
            message["From"] = settings.SMTP_FROM
            message["To"] = author_email
            message["Subject"] = subject
            message.set_content(body)

            try:
                smtp = SMTP(
                    hostname=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    use_tls=settings.SMTP_TLS,
                )
                await smtp.connect()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

                await smtp.send_message(message)
                await smtp.quit()

                print(
                    f"[Celery] Email sent to {author_email} about review (book={book_id}, user={user_id})"
                )
            except Exception as exc:
                print(f"[Celery] Failed to send email: {exc}")
                raise self.retry(exc=exc)


    asyncio.run(_send())
