import asyncio
import os
import socket
import subprocess
import signal
import asyncpg
from pathlib import Path
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

# Store tunnel process
_tunnel_process: subprocess.Popen | None = None


def _is_port_open(port: int, host: str = "localhost", timeout: float = 1.0) -> bool:
    """Check if port is open"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


def _wait_for_ports(ports: list[int], timeout: int = 60) -> bool:
    """Wait until ports are open"""
    logger = get_logger(__name__)
    import time
    start = time.time()

    while time.time() - start < timeout:
        all_open = all(_is_port_open(port) for port in ports)
        if all_open:
            return True
        time.sleep(1)
        logger.info("Waiting for tunnel connection... (%.0fs)", time.time() - start)

    return False


def start_dev_local_tunnel() -> bool:
    """Start SSM tunnel for dev-local environment"""
    global _tunnel_process
    logger = get_logger(__name__)

    script_path = Path(__file__).parent / "scripts" / "tunnel-ssm.sh"

    if not script_path.exists():
        logger.error("Tunnel script not found: %s", script_path)
        return False

    # Skip if ports are already open
    required_ports = [5433, 6380]  # AuthDB, Redis
    if all(_is_port_open(port) for port in required_ports):
        logger.info("Tunnel is already connected")
        return True

    logger.info("Starting SSM tunnel...")

    # Run tunnel script in background
    _tunnel_process = subprocess.Popen(
        [str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )

    # Wait for port connection
    if _wait_for_ports(required_ports, timeout=60):
        logger.info("SSM tunnel connected - AuthDB:5433, Redis:6380")
        return True
    else:
        logger.error("SSM tunnel connection timeout")
        stop_dev_local_tunnel()
        return False


def stop_dev_local_tunnel():
    """Stop tunnel process"""
    global _tunnel_process
    logger = get_logger(__name__)

    if _tunnel_process:
        logger.info("Stopping SSM tunnel...")
        try:
            os.killpg(os.getpgid(_tunnel_process.pid), signal.SIGTERM)
            _tunnel_process.wait(timeout=5)
        except Exception:
            try:
                os.killpg(os.getpgid(_tunnel_process.pid), signal.SIGKILL)
            except Exception:
                pass
        _tunnel_process = None
        logger.info("SSM tunnel stopped")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger = get_logger(__name__)
    logger.info("Starting up...")
    settings = get_settings()

    # Start tunnel for dev-local environment
    env = os.getenv("ENV", "")
    if env == "dev-local":
        if not start_dev_local_tunnel():
            raise RuntimeError("Failed to start SSM tunnel")

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

    # Clean up tunnel on shutdown
    if env == "dev-local":
        stop_dev_local_tunnel()

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
    # await ainitialize_redis(settings)  # TODO: ElastiCache TLS 설정 확인 필요
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
