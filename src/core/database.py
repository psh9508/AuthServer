from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.config import get_config

async_engine = None
async_session = None

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
    
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session