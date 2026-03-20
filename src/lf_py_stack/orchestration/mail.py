"""Thin helper functions to send emails via python"""

import logging
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Annotated

import typer


def send_mail(
    to: str,
    subject: str,
    body: str | Path,
    body_is_html: bool = False,
    smtp_server: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    from_name: str | None = None,
    attachments: list[Path] | None = None,
    use_tls: bool = True,
    use_ssl: bool = False,
    verbose: bool = False,
    log: logging.Logger | None = None,
):
    """
    Send an email with optional attachments.

    Raises if sending failed.

    Uses the following env variables, if no credentials are provided:
    - LFPY_MAIL_SMTP_SERVER
    - LFPY_MAIL_SMTP_PORT
    - LFPY_MAIL_USERNAME
    - LFPY_MAIL_PASSWORD
    """

    if log is None:
        log = logging.getLogger("orchestration")

    smtp_server, port, username, password = _prep_credentials_from_env_vars(
        smtp_server, port, username, password
    )

    if from_name is None:
        from_name = username

    msg = MIMEMultipart()
    msg["From"] = from_name
    msg["To"] = to
    msg["Subject"] = subject

    if isinstance(body, Path):
        body = body.read_text()

    if body_is_html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    if attachments:
        for attachment_path in attachments:
            if attachment_path.exists():
                with attachment_path.open("rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={attachment_path.name}",
                    )
                    msg.attach(part)
            else:
                typer.echo(
                    f"Warning: Attachment not found: {attachment_path}", err=True
                )

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.set_debuglevel(1 if verbose else 0)
            # TODO: redirect verbose output to logger
            if username == "" and password == "":
                log.info("Empty Username and pass, skipping login")
            else:
                server.login(username, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_server, port) as server:
            server.set_debuglevel(1 if verbose else 0)
            if use_tls:
                server.starttls()
            if username == "" and password == "":
                log.info("Empty Username and pass, skipping login")
            else:
                server.login(username, password)
            server.send_message(msg)


def _prep_credentials_from_env_vars(
    smtp_server: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
):
    """Fill credentials that were not provided from env vars or defaults."""

    smtp_server = smtp_server or os.getenv("LFPY_MAIL_SMTP_SERVER")
    if smtp_server is None:
        raise ValueError("Pass --smtp_server or set env var LFPY_MAIL_SMTP_SERVER")

    if port is None:
        port = int(os.getenv("LFPY_MAIL_SMTP_PORT", 587))

    if username is None:
        username = os.getenv("LFPY_MAIL_USERNAME", "")

    if password is None:
        password = os.getenv("LFPY_MAIL_PASSWORD", "")

    return smtp_server, port, username, password


# --------------------------------- Typer app -------------------------------- #

mail_app = typer.Typer(help="CLI tool to send emails via SMTP")


@mail_app.command()
def send(
    to: Annotated[
        str,
        typer.Option("--to", "-t", help="Recipient email address"),
    ],
    smtp_server: Annotated[
        str | None,
        typer.Option("--smtp-server", help="SMTP server address"),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option("--port", help="SMTP port"),
    ] = None,
    username: Annotated[
        str | None,
        typer.Option("--username", help="SMTP username"),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option("--password", help="SMTP password"),
    ] = None,
    from_name: Annotated[
        str | None,
        typer.Option(
            "--from", "-f", help="Sender email address (defaults to username)"
        ),
    ] = None,
    subject: Annotated[
        str,
        typer.Option("--subject", "-s", help="Email subject"),
    ] = "",
    body: Annotated[
        str | None,
        typer.Option("--body", "-b", help="Email body text"),
    ] = None,
    body_file: Annotated[
        Path | None,
        typer.Option(
            "--body-file",
            "-B",
            help="File containing email body",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
    body_is_html: Annotated[
        bool,
        typer.Option("--html", help="Body is HTML format"),
    ] = False,
    attachment: Annotated[
        list[Path] | None,
        typer.Option(
            "--attachment",
            "-a",
            help="Attachment file(s)",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
    use_ssl: Annotated[
        bool,
        typer.Option("--ssl", help="Use SSL (default is TLS)"),
    ] = False,
    use_tls: Annotated[
        bool,
        typer.Option("--tls", help="Use TLS (recommended to keep on)"),
    ] = True,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable SMTP debug output"),
    ] = False,
):
    """
    Send an email via SMTP.

    Uses the following env variables, if no credentials are provided:
    - LFPY_MAIL_SMTP_SERVER
    - LFPY_MAIL_SMTP_PORT
    - LFPY_MAIL_USERNAME
    - LFPY_MAIL_PASSWORD
    """

    body_to_use : str | Path
    if body_file is not None:
        assert body is None, "Provide either body or body_file"
        body_to_use = body_file
    elif body is not None:
        body_to_use = body
    else:
        body_to_use = ""

    try:
        send_mail(
            smtp_server=smtp_server,
            port=port,
            username=username,
            password=password,
            from_name=from_name,
            to=to,
            subject=subject,
            body=body_to_use,
            attachments=attachment,
            use_tls=use_tls,
            use_ssl=use_ssl,
            body_is_html=body_is_html,
            verbose=verbose,
        )
        typer.echo("✓ Email sent successfully!")
    except Exception as e:
        typer.echo(f"✗ Failed to send email: {e}", err=True)
        raise typer.Exit(1)


@mail_app.command()
def test(
    smtp_server: Annotated[
        str | None,
        typer.Option("--smtp-server", help="SMTP server address"),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option("--port", help="SMTP port"),
    ] = None,
    username: Annotated[
        str | None,
        typer.Option("--username", help="SMTP username"),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option("--password", help="SMTP password"),
    ] = None,
    use_ssl: Annotated[
        bool,
        typer.Option("--ssl", help="Use SSL (default is TLS)"),
    ] = False,
    use_tls: Annotated[
        bool,
        typer.Option("--tls", help="Use TLS (recommended to keep on)"),
    ] = True,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable SMTP debug output"),
    ] = False,
):
    """
    Test SMTP connection without sending an email.

    Uses the following env variables, if no credentials are provided:
    - LFPY_MAIL_SMTP_SERVER
    - LFPY_MAIL_SMTP_PORT
    - LFPY_MAIL_USERNAME
    - LFPY_MAIL_PASSWORD
    """

    smtp_server, port, username, password = _prep_credentials_from_env_vars(
        smtp_server, port, username, password
    )

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.set_debuglevel(1 if verbose else 0)
                server.login(username, password)
                typer.echo("✓ SSL connection successful!")
        else:
            with smtplib.SMTP(smtp_server, port) as server:
                server.set_debuglevel(1 if verbose else 0)
                if use_tls:
                    server.starttls()
                server.login(username, password)
                typer.echo(f"✓ Connection successful ({use_tls=})!")
    except Exception as e:
        typer.echo(f"✗ Connection failed: {e}", err=True)
        raise typer.Exit(1)
