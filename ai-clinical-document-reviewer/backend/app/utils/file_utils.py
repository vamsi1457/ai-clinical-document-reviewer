import os
import tempfile
from contextlib import contextmanager
from typing import Generator
from app.utils.logger import logger


@contextmanager
def temporary_file_context(suffix: str = "", content: bytes = b"") -> Generator[str, None, None]:
    """Creates a temporary file, writes initial content, yields its path, and guarantees deletion."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        if content:
            os.write(fd, content)
        os.close(fd)
        yield path
    finally:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError as e:
                logger.warning(f"Could not remove temporary file {path}: {str(e)}")
