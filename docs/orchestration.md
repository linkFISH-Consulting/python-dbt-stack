
# Orchestration

We now include some lightweight tools to orchestrate simple pipelines via hamilton.

To get started, create a python file as shown below, and then run it with python, providing paramters as needed.

```bash
python orchestration.py --help
python orchestration.py run
```

```python
# orchestration.py

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

```

Will produce the following output
(if env vars for email are set correctly, see `./orchestration.py mail --help`):

```raw
> python ./orchestration.py run
Running the following steps:
         ╷
  Step   │ Description
 ════════╪═══════════════════════════════════════════════════════════════════════════════
  step_a │ A dummy step
 ────────┼───────────────────────────────────────────────────────────────────────────────
  step_b │ Step that uses env vars and previous results
 ────────┼───────────────────────────────────────────────────────────────────────────────
  step_c │ To denote the sequence, make steps depende on previous ones via arguments.
         │ You do not _have to use_ `step_b` in here.
 ────────┼───────────────────────────────────────────────────────────────────────────────
  step_d │ We can also log everything we do (to send via email) and run cli commands
 ────────┼───────────────────────────────────────────────────────────────────────────────
  step_e │ Email example
         │ The send_mail function uses environment variables, and can send our log file.
         ╵

Hello from step_a
Hello from step_b
Current shell: /bin/zsh
Previous step result: All good
Hello from step_c
Hello from step_d
                              Orchestration run complete
         ╷        ╷
  Step   │ Status │ Log
 ════════╪════════╪═══════════════════════════════════════════════════════════════════
  step_a │ PASS   │ All good
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_b │ PASS   │ Also all good
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_c │ FAIL   │ Something went wrong
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_d │ PASS   │ total 408
         │        │ -rw-r--r--  1 paul  staff    1527 Mar 19 14:07 CHANGELOG.md
         │        │ -rw-r--r--@ 1 paul  staff     677 Mar 19 11:29 docker-compose.yml
         │        │ -rw-r--r--@ 1 paul  staff    3303 Mar 19 11:51 Dockerfile
         │        │ -rwxr-xr-x  1 paul  staff    1482 Feb  4 16:54 entrypoint.sh
         │        │ -rw-r--r--  1 paul  staff    1076 Dec  8 14:01 LICENSE
         │        │ -rw-r--r--@ 1 paul  staff    1873 Mar 19 13:13 pyproject.toml
         │        │ -rw-r--r--@ 1 paul  staff   10542 Mar 19 14:17 README.md
         │        │ -rw-r--r--  1 paul  staff    4941 Mar 19 14:18 requirements.txt
         │        │ drwxr-xr-x@ 3 paul  staff      96 Mar 19 11:19 src
         │        │ -rw-r--r--  1 paul  staff  157377 Mar 19 14:07 uv.lock
         │        │
 ────────┼────────┼───────────────────────────────────────────────────────────────────
  step_e │ PASS   │ Email sent successfully

```
