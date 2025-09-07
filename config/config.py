import os

_config = None

def load_config(environment: str = 'local'):
    import yaml
    global _config
    if _config is None:
        config_file_path = f'./config/config_{environment}.yml'
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
        with open(config_file_path, 'r', encoding='utf-8') as f:
            _config = yaml.safe_load(f)
        
        from dotenv import load_dotenv
        has_dotenv = load_dotenv() 

        if not has_dotenv:
            print(".env file not found or could not be loaded.")

        _replace_env_values(_config)
    return _config

def get_config():
    if _config is None:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return _config

def _replace_env_values(config):
    for key, value in config.items():
        if isinstance(value, dict):
            _replace_env_values(value)
        elif isinstance(value, str) and value.startswith('ENV_'):
            env_value = os.environ.get(value)
            if env_value is None:
                raise ValueError(f"Environment variable for {value} not found in .env file.")
            config[key] = env_value