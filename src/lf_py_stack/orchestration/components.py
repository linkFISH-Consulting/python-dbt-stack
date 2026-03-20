"""
Helper and Components. These are most likely to be accessed by users.
"""

import inspect
import logging
import os
import re
import subprocess
from pathlib import Path


def run_cli_command(
    command: str,
    env: dict[str, str] | None = None,
    log: logging.Logger | None = None,
    print_to_stdout: bool = True,
) -> tuple[int, str]:
    """Run a CLI command.

    Captures stdout/sterr lines as they appear and either prints them,
    or passes them into the provided logger. (See `get_logger` to write to console
    and files simultaneously)

    Optionally loads environment variables from a .env file
    """

    lines = []

    with subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge sterr into stdout
        text=True,
        bufsize=1,  # line-buffered
        env=env,
    ) as proc:
        try:
            if proc.stdout:
                for line in proc.stdout:
                    if log is not None:
                        log.info(line.rstrip(), extra={"log_to_cli": print_to_stdout})
                    elif print_to_stdout:
                        print(line, end="")
                    lines.append(line)
            else:
                return 1, "Failed to start process (no stdout available)"

        except Exception as e:
            return 1, f"Process execution failed: {str(e)}"

        finally:
            proc.wait()

    return proc.returncode, "".join(lines)


def get_logger(step_name: str | None = None) -> logging.Logger:
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
    log = logging.getLogger("orchestration")
    log.setLevel(os.environ.get("LFPY_LOG_LEVEL", "INFO"))
    file_path = os.environ.get("LFPY_LOG_FILE", None)

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
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.addFilter(SuppressCliFilter())
    log.addHandler(console_handler)

    return log


def truncate(text: str, first_lines: int = 10, last_lines: int = 5) -> str:
    """Get first x and last y lines of multiline text"""
    lines = text.splitlines()
    if len(lines) <= first_lines + last_lines:
        return text
    return "\n".join(lines[:first_lines] + ["..."] + lines[-last_lines:])
