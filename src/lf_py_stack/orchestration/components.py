"""
Helper and Components. These are most likely to be accessed by users.
"""

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.table import Table, box
from rich.terminal_theme import MONOKAI
from ruamel.yaml import YAML


def run_cli_command(
    command: str,
    env: dict[str, str] | None = None,
    log: logging.Logger | None = None,
    print_to_stdout: bool = True,
) -> tuple[int, str]:
    """Run a CLI command.

    Captures stdout/sterr lines as they appear and either prints them,
    or passes them into the provided logger. (Use our `get_logger` to write to
    console and files simultaneously)

    If no `env` is provided, the current environment variables will be used. (If you
    use our `run` cli wrapper, it has made variables from the .env available already.
    No need to load or pass the .env file again)
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


def truncate(text: str, first_lines: int = 10, last_lines: int = 5) -> str:
    """Get first x and last y lines of multiline text"""
    lines = text.splitlines()
    if len(lines) <= first_lines + last_lines:
        return text
    return "\n".join(lines[:first_lines] + ["..."] + lines[-last_lines:])


@dataclass
class PackageVersions:
    package: str
    version: str | None = None
    revision: str | None = None
    source_file: str | None = None


def get_dbt_versions(
    dbt_project_dir: Path | str | None = None,
) -> dict[str, PackageVersions]:
    """
    Get Versions of installed dbt packages from relevant yaml files.

    Returns a dict mapping package name to Details
    """

    # Create a dictionary to merge versions by package name
    merged: dict[str, PackageVersions] = {}
    for p in _get_dbt_versions(dbt_project_dir):
        if p.package not in merged.keys():
            # treat revision in packages.yml like versions
            if (
                p.source_file == "packages.yml"
                and p.version is None
                and p.revision is not None
            ):
                p.version = p.revision
                p.revision = None
            merged[p.package] = p
        else:
            existing = merged[p.package]
            if existing.version is None:
                existing.version = p.version
            if existing.revision is None:
                existing.revision = p.revision

    return merged


def _get_dbt_versions(
    dbt_project_dir: Path | str | None = None,
) -> list[PackageVersions]:
    """
    Helper to get versions of installed dbt packages from relevant yaml files,
    here we have a flat list, to solve the inconsistency between revision and version
    in packages vs package-lock
    """

    if dbt_project_dir is None:
        dbt_project_dir = os.getenv("DBT_PROJECT_DIR")

    if dbt_project_dir is None:
        raise OSError("DBT_PROJECT_DIR and DBT_PROFILES_DIR must be set.")
    else:
        dbt_project_dir = Path(dbt_project_dir)

    yaml = YAML(typ="safe", pure=True)
    yaml.preserve_quotes = True
    table_data = []

    # Main package version, from dbt_project.yml
    with (dbt_project_dir / "dbt_project.yml").open("r", encoding="utf-8") as file:
        data = yaml.load(file)
        table_data.append(
            PackageVersions(
                package=data.get("name", "not recognized"),
                version=data.get("version"),
                revision=data.get("revision"),
                source_file="dbt_project.yml",
            )
        )

    # Process packages.yml, but that file does not include dependencies, so check lock
    def _parse(yml_file: str):
        if not (dbt_project_dir / yml_file).exists():
            return

        with (dbt_project_dir / yml_file).open("r", encoding="utf-8") as file:
            for data in yaml.load(file).get("packages", []):
                if isinstance(data, dict):
                    table_data.append(
                        PackageVersions(
                            package=data.get(
                                "package", data.get("git", "not recognized")
                            ),
                            version=data.get("version"),
                            revision=data.get("revision"),
                            source_file=yml_file,
                        )
                    )
                else:
                    table_data.append(
                        PackageVersions(
                            package=str(data),
                            source_file=yml_file,
                        )
                    )

    _parse("packages.yml")
    _parse("package-lock.yml")

    return table_data


def log_dbt_versions(
    dbt_project_dir: Path | str | None = None,
    log: logging.Logger | None = None,
    print_to_stdout: bool = False,
    return_format: Literal["minimal", "plain", "colored", "html"] = "minimal",
    show_source_file=False,
):
    """
    Log Versions of installed dbt packages in various formats.

    return_format:
        - minimal: just name -> version
        - plain:   formatted as a table
        - colored: with colored columns
        - html:    render for email sending
    """

    package_versions = get_dbt_versions(dbt_project_dir)

    if return_format == "minimal":
        text = ""
        for idx, p in enumerate(package_versions.values()):
            text += f"{p.package} {p.version or p.revision}"
            if p.source_file and show_source_file:
                text +=f" (via {p.source_file})"
            if idx != len(package_versions.values()) -1 :
                text += "\n"

        if print_to_stdout:
            print(text)
    else:
        console = Console(
            record=True,
            file=open(os.devnull, "wt"),
        )
        table = Table(title="dbt Package Versions", box=box.SIMPLE)
        table.add_column("Package", style="cyan", overflow="fold")
        table.add_column("Version", style="green", min_width=9)
        table.add_column("Revision", style="green")
        if show_source_file:
            table.add_column("Source File")

        for p in package_versions.values():
            table.add_row(
                p.package,
                p.version,
                p.revision,
                p.source_file if show_source_file else None,
            )

        console.print(table)
        text = console.export_text(clear=False, styles=True)

        if print_to_stdout:
            print(text)

        if log is not None:
            log.info(f"\n{text}", extra={"log_to_cli": False})

        if return_format == "html":
            text = console.export_html(theme=MONOKAI)

    if return_format in ["plain", "html", "minimal"]:
        text = re.sub(r"(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~]", "", text)

    return text
