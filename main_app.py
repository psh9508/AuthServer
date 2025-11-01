import asyncio
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from config.config import load_config
from src.core.worker import Worker
from src.services.message_queue_service import MessageQueueService
from src.middleware.http_middleware import HttpMiddleware
from src.core.jwt_logic import JwtLogic
from src.core.database import init_db_session
from src.core.redis_core import ainitialize_redis

@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Starting up...")
    config = load_config()
    JwtLogic.initialize(config)
    print("Loaded configuration...")
    # await initializeDependencies(config)
    # print("Loaded Dependencies...")
    # await MessageQueueService.ainitialize_rabbitmq(config)
    # print("Initialized RabbitMQ client...")
    init_db_session()
    print("Initialized DB session...")
    # worker = Worker()
    # asyncio.create_task(worker.astart_worker())
    # print("The worker has been started...")
    yield
    
    # print("Shutting down...")
    # await worker.astop_worker()
    # print("The worker has been shut down...")


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

    
async def initializeDependencies(config):
    # await ainitialize_redis(config)
    await aconnect_to_db(config)
    

async def aconnect_to_db(config):
    global db_pool
    db_config = config['db']['postgres']
    user = db_config['user']
    password = db_config['password']
    host = db_config['host']
    port = db_config.get('port', 5432)
    database = db_config['database']

    try:
        db_pool = await asyncpg.create_pool(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        print("Connected to PostgreSQL")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        raise e