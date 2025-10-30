import os

from src.data_model.mq_config import MQConfig

_config = None
_mq_config: MQConfig

def load_config():
    import yaml
    global _config
    global _mq_config

    if _config is None:
        from dotenv import load_dotenv        
        load_dotenv()
        environment = os.environ.get('ENV', '')

        if environment == '':
            raise ValueError("ENV environment variable not set.")
        
        config_file_path = f'./config/config_{environment}.yml'
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
        with open(config_file_path, 'r', encoding='utf-8') as f:
            _config = yaml.safe_load(f)
       
        _replace_env_values(_config)

    # if not _config['server_name'] or not _config['exchange_name']:
    #     raise ValueError("Missing required configuration values: 'server_name' or 'exchange_name'")
    if not _config['jwt']['refresh_secret'] or not _config['jwt']['secret']:
        raise ValueError("Missing required configuration values: 'refresh_secret' or 'secret'")

    # _mq_config = MQConfig(server_name=_config['server_name'], exchange_name=_config['exchange_name'])
    return _config


def get_config():
    if _config is None:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return _config


def get_rabbitmq_config() -> MQConfig:
    if _mq_config is None:
        raise RuntimeError("RabbitMQ config is not set properly.")
    return _mq_config


def _replace_env_values(config):
    for key, value in config.items():
        if isinstance(value, dict):
            _replace_env_values(value)
        elif isinstance(value, str) and value.startswith('ENV_'):
            env_value = os.environ.get(value)
            if env_value is None:
                raise ValueError(f"Environment variable for {value} not found in .env file.")
            config[key] = env_value