import asyncpg
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi.concurrency import asynccontextmanager
from config.config import load_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    config = load_config()
    print("Loaded configuration...")
    await initializeDependencies(config)

    yield
    
    print("Shutting down...")

def get_main_app():
    app = FastAPI(lifespan=lifespan)
    return app

    
async def initializeDependencies(config):
    await _connect_to_redis(config)
    await _aconnect_to_db(config)

async def _connect_to_redis(config):
    global redis_client
    host = config['db']['redis']['host']
    port = config['db']['redis'].get('port', 6379)
    redis_url = f"redis://{host}:{port}"
    redis_client = await redis.Redis.from_url(redis_url, decode_responses=True)
    try:
        await redis_client.ping()
        print("Connected to Redis")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        raise e
    
async def _aconnect_to_db(config):
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