"""
StepResults are the objects we pass between hamiltons DAG nodes (functions)

We also have some helpers to log them.
"""

import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from rich.console import Console
from rich.table import Table, box


@dataclass
class StepResult:
    """
    Dataclass to transport status and outputs from one step to the next.

    This is useful because we mostly manifest data on disk, instead of passing
    it as loaded assets. The StepResults conveniently enable conditional operations in
    subsequent steps, e.g. by checking the status of previous ones.

    The "SKIP" status is used when the user choses to not run a particular step.
    In this case, we inject SKIP StepResults into hamiltons DAG via the `overrides` arg.
    """

    status: Literal["SKIP", "PASS", "FAIL"] = "PASS"
    message: str = ""
    name: str = ""

    def __post_init__(self):
        """Set the name automatically when instance is created"""
        if not self.name:  # Only set if name wasn't provided
            frame = inspect.currentframe()
            try:
                # Go up 2 frames: 1 for __post_init__, 1 for dataclass __init__
                self.name = frame.f_back.f_back.f_code.co_name  # type: ignore
            finally:
                del frame  # Avoid reference cycles


def log_step_nodes_table(
    steps: dict[str, Callable],
    title: str | None = None,
    show_dependencies: bool = True,
    show_docstrings: bool = True,
    log: logging.Logger | None = None,
    print_to_stdout: bool = True,
):
    """
    Print, log, and return a table of step nodes (the functions in hamiltons DAG)

    Optionally show each nodes dependencies and docstring.

    Args:
        steps: Dictionary of step names to their callable functions
        title: Optional title for the table
        show_dependencies: If True, shows dependencies column (default: True)
        show_docstrings: If True, shows description column (default: True)
        log: log into the provided logger, passes `extra={"log_to_cli": False}`
        print_to_stdout: Whether to show the table in stdout.

    Note:
        We chose to handle printing/logging separately here, because the log handler
        does not support colored output (yet)
    """
    if len(steps) == 0:
        print("No steps configured")
        return "No steps configured"

    console = Console()

    # https://rich.readthedocs.io/en/stable/appendix/box.html#appendix-box
    table = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD)

    table.add_column("Step", style="cyan")
    if show_dependencies:
        table.add_column("Depends on", style="magenta")
    if show_docstrings:
        table.add_column("Description", style="green")

    for step_name, step_func in steps.items():
        row = [step_name]

        if show_dependencies:
            sig = inspect.signature(step_func)
            params = "\n".join([param.name for param in sig.parameters.values()])
            row.append(params)

        if show_docstrings:
            description = inspect.getdoc(step_func) or "No documentation"
            row.append(description)

        table.add_row(*row, end_section=True)

    with console.capture() as capture:
        console.print(table)
    text = capture.get()

    if print_to_stdout:
        print(text)

    if log is not None:
        log.info(f"\n{text}", extra={"log_to_cli": False})

    return text


def log_step_results_table(
    steps: list[StepResult],
    title: str | None = None,
    log: logging.Logger | None = None,
    print_to_stdout: bool = True,
):
    """
    Print, log, and return a table of StepResults.

    Includes the step name, status, and message.

    Args:
        steps: list of StepResult
        title: Optional title for the table
        log: log into the provided logger, passes `extra={"log_to_cli": False}`
        print_to_stdout: Whether to show the table in stdout.

    Note:
        We chose to handle printing/logging separately here, because the log handler
        does not support colored output (yet)
    """
    console = Console()
    table = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD)

    table.add_column("Step", style="cyan")
    table.add_column("Status")
    table.add_column("Log")

    for step in steps:
        status_style = (
            "green"
            if step.status == "PASS"
            else "bold red"
            if step.status == "FAIL"
            else "dim white"
            if step.status == "SKIP"
            else "default"
        )
        table.add_row(
            step.name,
            f"[{status_style}]{step.status}[/]",
            step.message,
            end_section=True,
        )

    with console.capture() as capture:
        console.print(table)
    text = capture.get()

    if print_to_stdout:
        print(text)

    if log is not None:
        log.info(f"\n{text}", extra={"log_to_cli": False})

    return text
