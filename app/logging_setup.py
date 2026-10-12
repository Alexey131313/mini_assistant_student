"""Журналирование.

TODO (M1): настроить вывод логов и вернуть логгер приложения.
"""

import logging


def setup_logging(level: str = "INFO") -> logging.Logger:
    """TODO: настроить уровень и формат, вернуть логгер."""
    level = level.upper()
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return logging.getLogger("mini_assistant")
