"""
Allow easy logging from within steps

We have a helper to get a logger:
- the logger can be directly used like `logger.info("foobar")`
- the logger has a console and file handler, with levels and file path set from env var
- messages in the log file contain the step that obtained the logger via `get_logger`
"""

import inspect
import logging
import re
from pathlib import Path

from .env_vars import env


class LfPyLogger(logging.Logger):
    @property
    def log_file(self) -> Path | None:
        """Return the relevant file handler's path, if any."""
        for handler in self.handlers:
            if (
                handler.name == "lfpy_file_handler"
                and hasattr(handler, "baseFilename")
                and (fn := getattr(handler, "baseFilename")) is not None
            ):
                return Path(fn)
        return None


def get_logger(step_name: str | None = None) -> LfPyLogger:
    """Create and configure a logger with both console and file output.

    This allows us to prefix log messages by the step in which they are run,
    since each step gets their own logger.

    Args:
        step_name: Optional step name to include in log prefix. If not set,
        uses the name of the function calling this.

    Notes:
        - file_path can be set via env var LFPY_LOG_FILE
        - log level can be set via env var LFPY_LOG_LEVEL
        - you can skip console prints via `log.info("foo", extra={"log_to_cli": False})`
    """
    log = LfPyLogger("lfpy", level=env.logging.log_level)
    file_path = env.logging.log_file

    # Clear existing handlers to avoid duplication
    if log.hasHandlers():
        log.handlers.clear()

    # Create formatter with step name if provided
    if step_name is None:  # Only set if name wasn't provided
        frame = inspect.currentframe()
        try:
            # Go up 1 frame:
            step_name = frame.f_back.f_code.co_name  # type: ignore
        except Exception:
            step_name = "no_step"
        finally:
            del frame  # Avoid reference cycles

    # File handler
    # Create a formatter that strips ANSI codes
    class StripAnsiFormatter(logging.Formatter):
        def format(self, record):
            message = super().format(record)
            return re.sub(r"(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~]", "", message)

    if file_path is None or not Path(file_path).parent.is_dir():
        log.debug(f"Skipping log file creation because {file_path=} does not exist")
    else:
        file_handler = logging.FileHandler(file_path)
        file_handler.name = "lfpy_file_handler"
        file_handler.setFormatter(
            StripAnsiFormatter(
                f"[%(asctime)s %(levelname)s {step_name}] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        log.addHandler(file_handler)

    # Console handler
    # with an option so we can still get log-file only
    # log.info(f"Log-File Only", extra={"log_to_cli": False})
    class SuppressCliFilter(logging.Filter):
        def filter(self, record):
            return getattr(record, "log_to_cli", True)

    console_handler = logging.StreamHandler()
    console_handler.name = "lfpy_console_handler"
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.addFilter(SuppressCliFilter())
    log.addHandler(console_handler)

    return log
