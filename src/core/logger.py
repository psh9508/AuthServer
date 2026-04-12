def get_logger(name: str | None = None):
    import logging
    from src.config.settings import get_settings

    level = logging.INFO
    default_name = "AuthServer"

    try:
        settings = get_settings()
        level = getattr(logging, settings.logger.level.upper(), logging.INFO)
        default_name = settings.server_name
    except (RuntimeError, ValueError):
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
