from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parents[2]
ENVIRONMENTS_DIR = ROOT_DIR / "environments"
ENV_VAR_PATTERN = re.compile(r"\$\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|\$(?P<plain>[A-Za-z_][A-Za-z0-9_]*)")


class RedisConfig(BaseModel):
    host: str = Field(..., description="Redis hostname")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    prefix: str = Field(default="", description="Redis key prefix")


class PostgresConfig(BaseModel):
    host: str = Field(..., description="Postgres hostname")
    port: int = Field(default=5432, description="Postgres port")
    user: str = Field(..., description="Postgres user")
    password: str = Field(..., description="Postgres password")
    database: str = Field(..., description="Postgres database name")
    ssl_path: Optional[str] = Field(default=None, description="SSL certificate path")


class DatabaseConfig(BaseModel):
    redis: RedisConfig
    postgres: PostgresConfig


class RabbitMQConfig(BaseModel):
    host: str = Field(..., description="RabbitMQ hostname")
    port: int = Field(default=5672, description="RabbitMQ port")
    user: str = Field(..., description="RabbitMQ user")
    password: str = Field(..., description="RabbitMQ password")
    vhost: str = Field(default="/", description="RabbitMQ virtual host")


class JWTConfig(BaseModel):
    secret: str = Field(..., description="JWT secret key")
    refresh_secret: str = Field(..., description="JWT refresh secret key")


class SourceControlConfig(BaseModel):
    providers: list[str] = Field(default_factory=list, description="Source control providers")


class LoggerConfig(BaseModel):
    level: str = Field(default="INFO", description="Logging level")


class AppSettings(BaseModel):
    env: str = Field(..., description="Active runtime environment")
    config_path: Path = Field(..., description="Resolved config file path")
    server_name: str = Field(default="auth", description="Server name")
    exchange_name: Optional[str] = Field(default=None, description="RabbitMQ exchange name")
    db: DatabaseConfig
    rabbitmq: Optional[RabbitMQConfig] = Field(default=None)
    jwt: JWTConfig
    source_control: Optional[SourceControlConfig] = Field(default=None)
    logger: LoggerConfig = Field(default_factory=LoggerConfig)


def _resolve_environment_name() -> str:
    env_name = os.getenv("ENV")
    if env_name is not None and env_name.strip():
        return env_name.strip()

    raise ValueError(
        "Missing runtime environment name. Set ENV. "
        "A local .env file is optional and only used as a fallback during development."
    )


def _resolve_config_path(env_name: str) -> Path:
    config_path = ENVIRONMENTS_DIR / env_name / "config.yaml"
    if not config_path.is_file():
        available_envs = sorted(
            path.name for path in ENVIRONMENTS_DIR.iterdir() if path.is_dir()
        )
        raise FileNotFoundError(
            f"Config file not found for env='{env_name}': {config_path}. "
            f"Available environments: {', '.join(available_envs)}"
        )
    return config_path


def _load_config_yaml(config_path: Path) -> dict:
    yaml_content = config_path.read_text(encoding="utf-8")
    expanded_content = os.path.expandvars(yaml_content)

    unresolved_vars = sorted(
        {
            match.group("braced") or match.group("plain")
            for match in ENV_VAR_PATTERN.finditer(expanded_content)
        }
    )
    if unresolved_vars:
        unresolved_var_list = ", ".join(unresolved_vars)
        raise ValueError(
            f"Unresolved environment variables in {config_path}: {unresolved_var_list}"
        )

    return yaml.safe_load(expanded_content) or {}


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    load_dotenv(override=False)

    env_name = _resolve_environment_name()
    config_path = _resolve_config_path(env_name)
    raw_config = _load_config_yaml(config_path)

    return AppSettings(
        env=env_name,
        config_path=config_path,
        **raw_config,
    )
