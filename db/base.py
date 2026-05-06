from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from db.models import Base

engine = None
AsyncSessionFactory: async_sessionmaker[AsyncSession] | None = None


async def init_db(db_url: str) -> None:
    global engine, AsyncSessionFactory
    engine = create_async_engine(db_url, echo=False)
    AsyncSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session
