import logging
import re
import sys

# Masking pattern for potential keys or secrets
SECRET_PATTERN = re.compile(r'(key|token|auth|secret|password|bearer)[\s:=]+([^\s,;]+)', re.IGNORECASE)


class SensitiveDataFilter(logging.Filter):
    """Filter that sanitizes any accidental tokens or credentials from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = SECRET_PATTERN.sub(r'\1: [REDACTED]', record.msg)
        return True


def setup_logger(name: str = "clinical_reviewer") -> logging.Logger:
    """Configures and returns a structured logger for the clinical reviewer application."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger()
