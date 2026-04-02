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


def step_b(step_a: StepResult) -> StepResult:
    """Step that uses env vars and previous results"""
    print("Hello from step_b")
    print(f"Current shell: {os.environ.get('SHELL')}")
    print(f"Previous step result: {step_a.message}")
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


def step_d(step_c: StepResult) -> StepResult:
    """
    We can also log everything we do (to send via email) and run cli commands
    """
    log = get_logger()
    log.info("Hello from step_d")

    # by default, the run_cli_command uses your current environment variables,
    # which includes the .env file our main entrypoint has loaded (cli `run`)
    code, msg = run_cli_command("ls -l", log=log, print_to_stdout=False)
    return StepResult("PASS" if code == 0 else "FAIL", msg)


def step_e(step_d: StepResult) -> StepResult:
    """Email example
    The send_mail function uses environment variables, and can send our log file.
    """
    log = get_logger()
    log.info("Hello from step_e")
    try:
        send_mail(
            to="admin@example.com",
            from_name="orchestration@example.com",
            subject="Orchestration demo",
            body="Orchestration demo",
            attachments=log.log_file,
            # Note: the log file will only contain info from step_d and e,
            # because before, we used `print()` instead of `log.info()`
        )
        return StepResult("PASS", "Email sent successfully")
    except Exception as e:
        return StepResult("FAIL", str(e))


if __name__ == "__main__":
    # the app handles the cli interface and log file setup for us
    cli_app()
