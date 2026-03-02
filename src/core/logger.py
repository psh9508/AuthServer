

def get_logger(name: str | None = None):
    import logging
    from config.config import get_config, get_logger_config

    level = logging.INFO
    default_name = "AuthServer"

    try:
        logger_config = get_logger_config()
        level = getattr(logging, logger_config.level.upper(), logging.INFO)
    except RuntimeError:
        pass

    try:
        config = get_config()
        default_name = config.get("server_name", default_name)
    except RuntimeError:
        pass
    
    logger = logging.getLogger(name or default_name)
    logger.setLevel(level)
    
    if not logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    return logger
