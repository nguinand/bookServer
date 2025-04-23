import logging
import sys

def get_logger(name: str = "app") -> logging.Logger:
    """
    Returns a logger configured with a standard format.
    You can import and use this across modules.

    The name parameter lets you namespace your logs (e.g., main, db, auth).
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Set level (INFO by default, change as needed) Could be set with an ENV var
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Optional: avoid duplicate logs in interactive environments
        logger.propagate = False

    return logger
