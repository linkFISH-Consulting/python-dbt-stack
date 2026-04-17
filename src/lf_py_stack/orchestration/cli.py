"""
The cli currently works by importing the app we create at the end of the
orchestration script

Example
```python

from lf_py_stack.orchestration import cli_app

def step_a():
    pass

def step_b():
    pass

if __name__ == "__main__":
    # the app handles the cli interface and log file setup for us
    cli_app()
```
"""

import inspect
import os
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Annotated

import typer
from dotenv import dotenv_values
from hamilton import driver, telemetry
from hamilton.base import DictResult

from .config import config
from .duckdb import shrink_duckdb_command
from .mail import mail_app
from .steps import StepResult, log_step_nodes_table, log_step_results_table

telemetry.disable_telemetry()

cli_app = typer.Typer()


@cli_app.command()
def run(
    select: Annotated[
        list[str],
        typer.Option(
            "-s",
            "--select",
            help="Select steps to run via dbt-style syntax "
            "(step1, step1+, +step1, step2...step4). "
            "To run all steps: -s all",
        ),
    ] = [],
    # We want a way to pass things into individual steps from the cli
    step_args: Annotated[
        list[str],
        typer.Option(
            "-a",
            "--step-arg",
            help="Select a step and pass arguments (or data) into it. Usage: "
            "-a 'dbt_run: --select model_to_run' -a 'my_step: my_literal'",
        ),
    ] = [],
    skip: Annotated[
        list[str],
        typer.Option(
            "--skip",
            help="Skip a step. Combine with: -s all",
        ),
    ] = [],
    env_file: Annotated[
        Path | None,
        typer.Option(
            "--env-file",
            help="Load environment variables from this file",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
    log_level: Annotated[
        str | None,
        typer.Option(
            "--log-level",
            help="Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            envvar="LFPY_LOG_LEVEL",
        ),
    ] = None,
    log_file: Annotated[
        Path | None,
        typer.Option(
            "--log-file",
            help="Set the log file path. Wont log to file if not set.",
            envvar="LFPY_LOG_FILE",
        ),
    ] = None,
    # convenience: pass some dbt flags
    target: Annotated[
        str | None,
        typer.Option(
            "--target",
            help="Set the dbt target.",
            envvar="DBT_TARGET",
        ),
    ] = None,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Set the dbt profile.",
            envvar="DBT_PROFILE",
        ),
    ] = None,
):
    """
    Run the orchestration pipeline.
    """

    dotenv = dict(os.environ)
    if env_file:
        dotenv.update(
            {k: v for k, v in dotenv_values(env_file).items() if v is not None}
        )

    # We have no standardized handling for dbt variables yet.
    if target is not None:
        dotenv["DBT_TARGET"] = target
    if profile is not None:
        dotenv["DBT_PROFILE"] = profile

    os.environ.update(dotenv)  # Merge back

    # For logging, we have standardized helpers to set and get
    if log_level is not None:
        config.env.logging.log_level = log_level
    if log_file is not None:
        config.env.logging.log_file = log_file

    # as of now, we always invoke the app from a main module.
    # if this changes, we have to pass it via the app or an option
    driver = _get_driver(module="__main__")
    steps = _module_steps(module="__main__", driver=driver)
    step_names = [str(s) for s in steps.keys()]

    _steps_to_run = set()
    for pattern in select or []:
        matched = _parse_select_pattern(pattern.strip(), step_names)
        _steps_to_run.update(matched)
    steps_to_run = [
        s for s in step_names if s in _steps_to_run
    ]  # lets keep this ordered

    # Parse Arguments that should be available in individual steps.
    # Save into config so steps can retreive them
    # and automatically enable them as if they were specified with --select
    config.step_args = _parse_step_arguments(
        step_args=step_args, valid_step_names=step_names
    )
    for s in config.step_args.keys():
        if s not in steps_to_run:
            steps_to_run.append(s)

    # Apply skip
    steps_to_run = [s for s in steps_to_run if s not in skip]

    if not steps_to_run:
        print("Nothing to run. Consider using `-s all`")
        raise typer.Exit()

    print("Running the following steps:")
    log_step_nodes_table(
        steps={sn: steps[sn] for sn in steps_to_run},
        show_dependencies=False,
        show_docstrings=True,
        print_to_stdout=True,
    )

    # overrides allow us to avoid invoking steps from the DAG
    overrides = {
        s: StepResult("SKIP", "Skipped via CLI", name=s)
        for s in step_names
        if s not in steps_to_run
    }

    # TODO: readd later as its own command
    # try:
    #     driver.display_all_functions(output_file_path=Path("./logs/dag.png"))
    # except Exception:
    #     pass

    step_results: dict[str, StepResult] = driver.execute(
        final_vars=steps_to_run,  # type: ignore
        overrides=overrides,
    )

    log_step_results_table(
        steps=list(step_results.values()) + list(overrides.values()),
        title="Orchestration run complete",
        print_to_stdout=True,
    )


@cli_app.command(name="list")
def list_steps():
    """List configured steps."""
    driver = _get_driver("__main__")
    steps = _module_steps("__main__", driver)

    log_step_nodes_table(
        steps,
        show_dependencies=True,
        show_docstrings=True,
        print_to_stdout=True,
    )


cli_app.add_typer(mail_app, name="mail")
cli_app.command(name="shrink-duckdb")(shrink_duckdb_command)


# ---------------------------------------------------------------------------- #
#                  Helper functions (not part of Hamilton DAG)                 #
# ---------------------------------------------------------------------------- #


def _get_driver(module: ModuleType | str):
    if isinstance(module, str):
        module = sys.modules[module]
    return driver.Driver({}, module, adapter=DictResult())


def _module_steps(
    module: ModuleType | str, driver: driver.Driver
) -> dict[str, Callable]:
    """Get all steps (functions without underscores) in the current file.

    - Only inlcudes functions that are in the DAG
    - Sorted by appearance in the module (not in the DAG)
    """
    if isinstance(module, str):
        module = sys.modules[module]
    functions = [
        (name, obj, inspect.getsourcelines(obj)[1])
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if name in driver.graph.nodes and not name.startswith("_")
    ]

    # We do not allow a step name "all" because it is reserved as a cli argument
    for s in functions:
        if s[0] == "all":
            raise ValueError("Invalid Name for step: 'all' is reserved.")

    # Sort by line number and return names and functions
    sorted_functions = sorted(functions, key=lambda x: x[2])
    # step_names = [name for name, _, _ in sorted_functions]
    # step_functions = [func for _, func, _ in sorted_functions]
    return {s[0]: s[1] for s in sorted_functions}


def _parse_select_pattern(pattern: str, steps: list[str]) -> set[str]:
    """Transform selection patterns into a list of steps to run."""
    if not pattern:
        return set()

    # all → all steps
    if pattern == "all":
        return set(steps)

    # Step range: step2...step4
    if "..." in pattern:
        parts = pattern.split("...")
        if len(parts) != 2:
            typer.echo(
                f"Error: Invalid range syntax '{pattern}'. Use: start...end", err=True
            )
            raise typer.Exit(1)
        start, end = parts
        try:
            i = steps.index(start.strip())
            j = steps.index(end.strip())
        except ValueError:
            typer.echo(
                f"Error: step '{start.strip() or end.strip()}' not found in pipeline.",
                err=True,
            )
            raise typer.Exit(1)
        return set(steps[i : j + 1])

    # +step1 → from start to step1
    if pattern.startswith("+") and not pattern.endswith("+"):
        target = pattern[1:]
        if target not in steps:
            typer.echo(f"Error: step '{target}' not found in pipeline.", err=True)
            raise typer.Exit(1)
        idx = steps.index(target)
        return set(steps[: idx + 1])

    # step1+ → from step1 to end
    if pattern.endswith("+") and not pattern.startswith("+"):
        target = pattern[:-1]
        if target not in steps:
            typer.echo(f"Error: step '{target}' not found in pipeline.", err=True)
            raise typer.Exit(1)
        idx = steps.index(target)
        return set(steps[idx:])

    # step1 → only step1
    if pattern in steps:
        return {pattern}
    else:
        typer.echo(f"Error: step '{pattern}' not found in pipeline.", err=True)
        raise typer.Exit(1)


def _parse_step_arguments(
    step_args: list[str],
    valid_step_names: list[str] | None = None,
):
    """
    Transform a list of step_arguments into a mapping from step_name to arg.

    Expects each provided string to have the form `step_name:value`
    where `step_name` becomes the mapping key.

    Optionally, we check that the provided step_names are valid, and raise otherwise.
    """

    res: dict[str, str] = {}

    for step_arg in step_args:
        key, sep, value = step_arg.partition(":")
        key = key.strip()
        # keep payload as provided, except trimming one leading space after ':'
        value = value.lstrip() if sep else ""
        res[key] = value

    if valid_step_names is not None:
        invalid_steps = [s for s in res.keys() if str(s) not in valid_step_names]
    else:
        invalid_steps = []

    if len(invalid_steps) != 0:
        raise ValueError(
            f"Steps {invalid_steps} were not recognized. Available: {valid_step_names}"
        )

    return res
