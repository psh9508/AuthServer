import asyncio
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from src.config.settings import get_settings
from src.core.worker import Worker
from src.services.message_queue_service import MessageQueueService
from src.middleware.http_middleware import HttpMiddleware
from src.core.jwt_logic import JwtLogic
from src.core.database import init_db_session
from src.core.redis_core import ainitialize_redis
from src.core.logger import get_logger

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger = get_logger(__name__)
    logger.info("Starting up...")
    settings = get_settings()
    logger = get_logger(__name__)
    JwtLogic.initialize(settings)
    logger.info("Loaded configuration...")
    await initializeDependencies(settings)
    logger.info("Loaded Dependencies...")
    # await MessageQueueService.ainitialize_rabbitmq(settings)
    # logger.info("Initialized RabbitMQ client...")
    init_db_session()
    logger.info("Initialized DB session...")
    # worker = Worker()
    # asyncio.create_task(worker.astart_worker())
    # logger.info("The worker has been started...")
    yield

    # logger.info("Shutting down...")
    # await worker.astop_worker()
    # logger.info("The worker has been shut down...")


def get_main_app():
    app = FastAPI(lifespan=lifespan)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(HttpMiddleware)
    return app

    
async def initializeDependencies(settings):
    await ainitialize_redis(settings)
    await aconnect_to_db(settings)


async def aconnect_to_db(settings):
    logger = get_logger(__name__)
    global db_pool
    pg_config = settings.db.postgres
    user = pg_config.user
    password = pg_config.password
    host = pg_config.host
    port = pg_config.port
    database = pg_config.database

    try:
        db_pool = await asyncpg.create_pool(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        logger.info("Connected to PostgreSQL")
    except Exception as e:
        logger.exception("Failed to connect to PostgreSQL: %s", e)
        raise e
