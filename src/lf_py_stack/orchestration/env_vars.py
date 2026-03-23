"""
Unified place for reading / writing environment variables we use in _our_ helpers.

Why not just use env vars as is?
- robust typing and checks
- all env vars are in one place
- easier to refactor, and later add a config class if needed
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal, cast


@dataclass
class LoggingVars:
    """
    Env Variables relevant for logging.

    - LFPY_LOG_LEVEL
    - LFPY_LOG_FILE
    """

    @property
    def log_level(self) -> Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        lvl = os.environ.get("LFPY_LOG_LEVEL", "INFO").upper()

        if lvl not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Unrecognized log level: {lvl}")
        return cast(Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], lvl)

    @log_level.setter
    def log_level(self, lvl: str):
        lvl = lvl.upper()
        if lvl not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Unrecognized log level: {lvl}")
        os.environ["LFPY_LOG_LEVEL"] = lvl

    @property
    def log_file(self) -> Path | None:
        path = os.environ.get("LFPY_LOG_FILE", None)
        if path is None:
            return None
        return Path(path)

    @log_file.setter
    def log_file(self, path: Path | str):
        os.environ["LFPY_LOG_FILE"] = str(Path(path).absolute())


@dataclass
class MailVars:
    """
    Env Variables relevant for our mail wrapper.

    - LFPY_MAIL_SMTP_SERVER
    - LFPY_MAIL_SMTP_PORT
    - LFPY_MAIL_USERNAME
    - LFPY_MAIL_PASSWORD (or LFPY_MAIL_PASSWORD_FILE)
    """

    def get_defaults_from_env_vars(
        self,
        smtp_server: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> tuple[str, int, str, str]:
        """Fill credentials that were not provided from env vars or defaults."""

        smtp_server = smtp_server or os.getenv("LFPY_MAIL_SMTP_SERVER", None)
        if smtp_server is None:
            raise ValueError("Pass --smtp_server or set env var LFPY_MAIL_SMTP_SERVER")

        if port is None:
            port = self.smtp_port

        if username is None:
            username = self.username

        if password is None:
            password = self.password

        return smtp_server, port, username, password

    @property
    def smtp_server(self) -> str:
        server = os.environ.get("LFPY_MAIL_SMTP_SERVER", "")
        return server

    @smtp_server.setter
    def smtp_server(self, server: str):
        os.environ["LFPY_MAIL_SMTP_SERVER"] = server

    @property
    def smtp_port(self) -> int:
        port_str = os.environ.get("LFPY_MAIL_SMTP_PORT", "587")
        return int(port_str)

    @smtp_port.setter
    def smtp_port(self, port: int | str):
        os.environ["LFPY_MAIL_SMTP_PORT"] = str(port)

    @property
    def username(self) -> str:
        return os.environ.get("LFPY_MAIL_USERNAME", "")

    @username.setter
    def username(self, username: str):
        os.environ["LFPY_MAIL_USERNAME"] = username

    @property
    def password(self) -> str:
        password = os.environ.get("LFPY_MAIL_PASSWORD", None)
        if password is None:
            password = os.environ.get("LFPY_MAIL_PASSWORD_FILE", "")
        return password

    @password.setter
    def password(self, password: str):
        os.environ["LFPY_MAIL_PASSWORD"] = password


@dataclass
class EnvVars:
    logging: ClassVar[LoggingVars] = LoggingVars()
    mail: ClassVar[MailVars] = MailVars()


# singleton
env = EnvVars()
