"""
Helper and Components. These are most likely to be accessed by users.
"""

import logging
import subprocess


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
