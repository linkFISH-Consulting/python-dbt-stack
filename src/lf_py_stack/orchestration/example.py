"""
Should become part of the documentation.
"""

import os

from lf_py_stack.orchestration import (
    StepResult,
    cli_app,
    get_logger,
    run_cli_command,
    send_mail,
)


def step_a() -> StepResult:
    """A dummy step"""
    print("Hello from step_a")
    return StepResult("PASS", "All good")


def step_b(step_a: StepResult, env: dict) -> StepResult:
    """Step that uses env vars and previous results"""
    print("Hello from step_b")
    print(f"Current shell: {env.get('SHELL')}")
    print(f"Current shell: {os.environ.get('SHELL')}")
    print(f"Previous step restul: {step_a.message}")
    return StepResult("PASS", "Also all good")


def step_c(step_b: StepResult) -> StepResult:
    """
    To denote the sequence, make steps depende on previous ones via arguments.
    You do not _have to use_ `step_b` in here.
    """
    print("Hello from step_c")
    try:
        _will_fail = 1 / 0
        return StepResult("PASS", "All good")
    except ZeroDivisionError:
        return StepResult("FAIL", "Something went wrong")


def step_d(step_c: StepResult, env: dict) -> StepResult:
    """
    We can also log everything we do (to send via email) and run cli commands
    """
    log = get_logger()
    log.info("Hello from step_d")

    # PS @ SM: I noticed now we could simply pass os.environ, and do not need env
    # as an arg at all. would this be a better pattern? We set some variables
    # in the typer app, like log file path
    code, msg = run_cli_command("ls -l", log=log, env=env, print_to_stdout=False)
    return StepResult("PASS" if code == 0 else "FAIL", msg)


def step_e(step_d: StepResult) -> StepResult:
    """Email example
    The send_mail function uses environment variables, and can send our log file.
    """
    try:
        # send_mail command looks at os.environ
        send_mail(
            to="paul.spitzner@linkfish.eu",
            from_name="orchestration@example.com",
            subject="Orchestration demo",
            body="Orchestration demo",
        )
        return StepResult("PASS", "Email sent successfully")
    except Exception as e:
        return StepResult("FAIL", str(e))


if __name__ == "__main__":
    # the app handles the cli interface and log file setup for us
    cli_app()
