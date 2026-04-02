
# Linkfish Utilities (Python)
**Including DBT and Python Stack using UV**

The idea is to have one central reference for all our Python dependencies, DBT being one of them.
UV makes this possible because it allows us to manage Python packages via a central lock file (`uv.lock`), which can be updated conveniently, as new versions of dependencies are released.

## Installation

The steps below illustrate how to install the package directly on your local machine, using uv or pip.
(Other install methods include [docker](/docs/deploy_with_docker.md) and [conda](/docs/deploy_with_conda.md))

**using uv** and a dedicated venv (recommended)

- [Get UV](https://docs.astral.sh/uv/getting-started/installation/)

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

## Orchestration

We now include tools to orchestrate simple workflows.
They are written as simple python functions and respect .env files.

[See here](/docs/orchestration.md)


## Further Reading

- [Updating our dependencies](/docs/updating_dependencies.md)
- [UV Cheat Sheet](https://ricketyrick.github.io/uv_cheat_sheet/uv-cheat-sheet.html)
- [Using UV and Conda together](https://medium.com/@datagumshoe/using-uv-and-conda-together-effectively-a-fast-flexible-workflow-d046aff622f0)
    TLDR: Use Conda for heavy, non-native (cpp) dependencies like pytorch.
- [UV Discovery of Python Envs (including Conda)](https://docs.astral.sh/uv/pip/environments/#discovery-of-python-environments)
