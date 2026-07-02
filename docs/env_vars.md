# Environment Variables

The orchestration CLI, and some of our provided python components, make use of environment variables.


## Orchestration

Relevant for the `run` command.

| Variable             | CLI `run` argument    | Default      | Description                                            |
|----------------------|-----------------------|--------------|--------------------------------------------------------|
| `LFPY_LOG_LEVEL`     | `--log-level`         | `"INFO"`     | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Raises `ValueError` if an invalid level is supplied. |
| `LFPY_LOG_FILE`      | `--log-file`          | *not set*    | Path to the log file. When omitted, logging goes to stdout / CLI only. |
| `LFPY_WARN_EXIT_1`   | —                     | *not set*    | When truthy (e.g. `"1"`), causes the CLI to return exit code **1** if any step has status `WARN`. Without this variable, `WARN` is displayed but does not affect the exit code. |

## dbt

Relevant when running dbt inside an orchestration steps.
The CLI arguments are just for convenience, so orchestration runs are closer to calling dbt directly.

| Variable          | CLI `run` argument    | Default  | Description                                        |
|-------------------|-----------------------|----------|----------------------------------------------------|
| `DBT_TARGET`      | `--target`            | *not set* | dbt target to use.                                  |
| `DBT_PROFILE`     | `--profile`           | *not set* | dbt profile to use.                                 |
| `DBT_PROJECT_DIR` | —                     | *not set* | Path to the dbt project directory (required for component `get_dbt_versions`). Raises `OSError` if unset. |

## Mail

Relevant in the `mail` command, and the `send_mail` component.

| Variable                  | CLI argument    | Default  | Description                                                |
|---------------------------|-----------------------|----------|------------------------------------------------------------|
| `LFPY_MAIL_SMTP_SERVER`   | —                     | *not set* | SMTP server address. **Required** — raises `ValueError` if not configured. |
| `LFPY_MAIL_SMTP_PORT`     | —                     | `"587"`  | SMTP server port (converted to int internally).            |
| `LFPY_MAIL_USERNAME`      | —                     | `""`     | SMTP username.                                             |
| `LFPY_MAIL_PASSWORD`      | —                     | *not set* | SMTP password. Falls back to `LFPY_MAIL_PASSWORD_FILE` if unset. |
| `LFPY_MAIL_PASSWORD_FILE` | —                     | `""`     | Path to a file containing the SMTP password (fallback for `LFPY_MAIL_PASSWORD`). |

