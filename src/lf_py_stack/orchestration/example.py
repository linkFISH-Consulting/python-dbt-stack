"""
Should become part of the documentation.
"""

from lf_py_stack.orchestration import StepResult, cli_app, get_logger, run_cli_command


def step_a() -> StepResult:
    """A dummy step"""
    print("Hello from step_a")
    return StepResult("PASS", "All good")


def step_b(step_a: StepResult, env: dict) -> StepResult:
    """Step that uses env vars and previous results"""
    print("Hello from step_b")
    print(f"Current shell: {env.get('SHELL')}")
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
    code, msg = run_cli_command("ls -l", log=log, env=env, print_to_stdout=False)
    return StepResult("PASS" if code == 0 else "FAIL", msg)


if __name__ == "__main__":
    # the app handles the cli interface and log file setup for us
    cli_app()
