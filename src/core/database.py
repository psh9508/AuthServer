from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from config.config import get_config
from typing import Optional

async_engine: Optional[AsyncEngine] = None
async_session: Optional[async_sessionmaker[AsyncSession]] = None

def init_db_session():
    global async_engine, async_session
    
    config = get_config()
    db_config = config['db']['postgres']
    
    DATABASE_URL = (
        f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config.get('port', 5432)}/{db_config['database']}"
    )
    
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )
    
    async_session = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if async_session is None:
        raise RuntimeError("Database session not initialized. Call init_db_session() first.")
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
        finally:
            await session.close()