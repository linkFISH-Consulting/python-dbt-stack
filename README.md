
# Linkfish Utilities (Python)
**Including DBT and Python Stack using UV**

The idea is to have one central reference for all our Python dependencies, DBT being one of them.
UV makes this possible because it allows us to manage Python packages via a central lock file (`uv.lock`), which can be updated conveniently, as new versions of dependencies are released.

## Stack on Host

**using uv** and a dedicated venv

```bash
# create venv in your project dir
uv venv --python 3.12

# activate, linux
source ./.venv/bin/activate

# win
.venv\Scripts\activate

# install latest
uv pip install -r requirements.txt "git+https://github.com/linkFISH-Consulting/python-dbt-stack"

# or a specific version
uv pip install -r requirements.txt "git+https://github.com/linkFISH-Consulting/python-dbt-stack@v0.1.6"
```

**using pip**

```bash
python -m pip install "git+https://github.com/linkFISH-Consulting/python-dbt-stack"
```

## Stack in Docker Container

The container provides a full-fledged Python and DBT environment.

To build the container and run commands:

```bash
# get the latest image
docker pull ghcr.io/linkfish-consulting/python-dbt-stack:latest
# ... or a specific version
docker pull ghcr.io/linkfish-consulting/python-dbt-stack:v0.1.4

# create a tag, to access more conveniently
docker tag ghcr.io/linkfish-consulting/python-dbt-stack:v0.1.4 lf-py-stack

# run a command as the default non-root user (lf_admin)
docker run --rm -it lf-py-stack dbt --version
```

Usually you will need to mount data and project folders into the container via the `--volume` command:

```bash
docker run -it --rm --volume /coasti:/coasti lf-py-stack dbt --version
```

If you want to run as the root user, the usual `-u root` will not be sufficient, because we fix permissions and then drop to lf_admin.

```bash
# skip our entrypoint to run as root
docker run -it --rm -u root --entrypoint="" lf-py-stack bash
```

### Environement Variables

The Container supports the following environment variables.
Specify as e.g. `docker run -e EXTRA_GIDS=1002,1003`

- `PUID` set the user ID for lf_admin
- `GUID` set the group ID for lf_admin
- `EXTRA_GIDS` add lf_admin to extra groups, e.g. to be able to read from folder mounts owned by other users.


### Docker Compose

For a more involved setup:

```yaml
# docker-compose.yml
services:
    lf-py-stack:
        image: ghcr.io/linkfish-consulting/python-dbt-stack:latest
        # other settings, e.g.
        environment:
            - PUID: 1001
            - GUID: 1001
        volumes:
            - /coasti/data/:/coasti/data/
            - /coasti/products/haushaltplus/:/coasti/products/haushaltplus/
```

then run with
```bash
docker compose -f /path/to/docker-compose.yml run -it --rm lf-py-stack dbt --version
```

Often you will need some setup, like loading environment variables inside the container.
Then, it can be helpful to define an init command that can be reused:

```bash
INIT_CMD="set -a; source ./config/.env; set +a;"
docker run -it --rm --workdir /coasti/products/haushaltplus \
    lf-py-stack bash -c "$INIT_CMD dbt version"
```

## Stack with Conda

We keep the requirements.txt up to date with _locked_ Versions of all packages,
so you can simply include it in your Conda environment.

Once we establish releases, we will have a specific URL for each version of our
`lf_python_utils`, and by pinning that one, you will also pin dependencies.

```yaml
# environment.yml

# create env via:
# conda env create -f environment.yml -n my_env_name
name: dbt_playground
channels:
  - conda-forge
dependencies:
  - python=3.12
  - pip
  - pip:
    - -r https://raw.githubusercontent.com/linkFISH-Consulting/python-dbt-stack/main/requirements.txt
```

## Orchestration

We now include some lightweight tools to orchestrate simple pipelines via hamilton.

To get started, create a python file as shown below, and then run it with python, providing paramters as needed.

```bash
python orchestration.py --help
python orchestration.py run
```

```python
# orchestration.py

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

def step_d(step_c : StepResult, env: dict) -> StepResult:
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
```

Will produce the following output:

```raw
> python ./orchestration.py run
Running the following steps:
         ╷
  Step   │ Description
 ════════╪════════════════════════════════════════════════════════════════════════════
  step_a │ A dummy step
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_b │ Step that uses env vars and previous results
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_c │ To denote the sequence, make steps depende on previous ones via arguments.
         │
         │ You do not _have to use_ `step_b` in here.
 ────────┼────────────────────────────────────────────────────────────────────────────
  step_d │ We can also log everything we do (to send via email) and run cli commands
         ╵

Hello from step_a
Hello from step_b
Current shell: /bin/zsh
Previous step restul: All good
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
  step_d │ PASS   │ total 392
         │        │ -rw-r--r--@ 1 paul  staff    1527 Mar 19 13:09 CHANGELOG.md
         │        │ -rw-r--r--@ 1 paul  staff     677 Mar 19 11:29 docker-compose.yml
         │        │ -rw-r--r--@ 1 paul  staff    3303 Mar 19 11:51 Dockerfile
         │        │ -rwxr-xr-x  1 paul  staff    1482 Feb  4 16:54 entrypoint.sh
         │        │ -rw-r--r--  1 paul  staff    1076 Dec  8 14:01 LICENSE
         │        │ -rw-r--r--@ 1 paul  staff    1873 Mar 19 13:13 pyproject.toml
         │        │ -rw-r--r--@ 1 paul  staff    5053 Mar 19 13:25 README.md
         │        │ -rw-r--r--  1 paul  staff    4941 Jan 14 13:38 requirements.txt
         │        │ drwxr-xr-x@ 3 paul  staff      96 Mar 19 11:19 src
         │        │ -rw-r--r--  1 paul  staff  157377 Mar 19 11:26 uv.lock
         │        │
         ╵        ╵
```

## Updating Dependencies in this Repo

- Clone to your Device

- [Get UV](https://docs.astral.sh/uv/getting-started/installation/)

- Check `pyproject.toml` if you want to update min/max versions

- Check what package updates are available
```bash
uv lock --dry-run --upgrade
# or
uv tree --outdated
```

- Update dependencies and the `uv.lock`
```bash
uv sync --upgrade
```

- Put the changes into `requirements.txt`
```bash
uv pip compile pyproject.toml -o requirements.txt
```

- Update changelog, and possibly version number in pyproject.toml

- Open PR

- Note: Dont forget to run `uv sync`, even after you only bumped our own version `pyproject.toml`.


## Useful UV Commands

```bash
# Find out which python exe uv will use (could be system, conda, venv, ...)
uv python find
```

## Building the container locally

```bash
docker compose build
docker run -it --rm lf-py-stack bash
```

## Furhter Reading

- [UV Cheat Sheet](https://ricketyrick.github.io/uv_cheat_sheet/uv-cheat-sheet.html)
- [Using UV and Conda together](https://medium.com/@datagumshoe/using-uv-and-conda-together-effectively-a-fast-flexible-workflow-d046aff622f0)
    TLDR: Use Conda for heavy, non-native (cpp) dependencies like pytorch.
- [UV Discovery of Python Envs (including Conda)](https://docs.astral.sh/uv/pip/environments/#discovery-of-python-environments)
