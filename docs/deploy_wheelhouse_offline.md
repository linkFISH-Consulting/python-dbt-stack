# Deploying using the wheelhouse

> [!NOTE]
> Currently only applies to windows and the 64bit x86 platform

For each release, we create a single-file wheelhouse of the stack, so you can install on windows without an internet connection.

To deploy:

- Download the wheelhouse for your architecture and python version
- Extract the zip. Here we assume you extracted to `D:\linkFISH\apps\lf_py_stack\`
- Run the commands below:
  - they link against the specified python version (e.g. [portable](https://github.com/astral-sh/python-build-standalone)). Here we use `D:\linkFISH\apps\python.exe`
  - create and activate a new venv in the current directory
  - install from the wheelhouse without online lookup

```pwsh
uv venv --python "D:\linkFISH\apps\python\python.exe"
.venv\Scripts\activate

uv pip sync "D:\linkFISH\apps\lf_py_stack\requirements.txt" `
  --find-links "D:\linkFISH\apps\lf_py_stack\wheels" `
  --no-index

uv pip install lf_py_stack `
  --find-links "D:\linkFISH\apps\lf_py_stack\wheels" `
  --no-index
```


# Installing dbt as a uv tool

A common usecase is that we just want a working dbt installation that uses a standalone python version, and our `lf_py_stack` to pin versions.

- Download the latest wheelhouse from our [release page](https://github.com/linkFISH-Consulting/python-dbt-stack/releases)
- Get the standlone python that matches the major version (currently 3.12) from [the astral repo](https://github.com/astral-sh/python-build-standalone/releases)
- To set the installtion path for dbt, use the env vars `UV_TOOL_DIR` and `UV_TOOL_BIN_DIR`, see the [docs](https://docs.astral.sh/uv/reference/storage/#tools)

```pwsh
$env:UV_TOOL_DIR="D:\linkFISH\user_config\uv\tools"
$env:UV_TOOL_BIN_DIR="D:\linkFISH\user_config\uv\bin"
uv tool install `
    --python "D:\linkFISH\apps\python\python.exe" `
    --find-links "D:\linkFISH\apps\lf_py_stack\wheels\" `
    --no-index `
    --with lf_py_stack `
    dbt-core
```

> [!NOTE]
> Der MDS Installer platziert die .exe nicht in `\user_config` sondern in `\apps\dbt`
