# Deploying using the wheelhouse

For each release, we create a single-file wheelhouse of the stack, so you can install on windows without an internet connection.

To deploy:

- Download the wheelhouse for your architecture and python version
- Extract the zip and name it `wheelhouse`
- Run the commands below:
  - they link against the specified python version (e.g. [portable](https://github.com/astral-sh/python-build-standalone))
  - create and activate a new venv in the current directory
  - install from the wheelhouse without online lookup

```pwsh
uv venv --python portable\python\python.exe
.venv\Scripts\activate

uv pip sync wheelhouse\requirements.txt `
  --find-links wheelhouse\wheels `
  --python .venv\Scripts\python.exe `
  --no-index
  
uv pip install lf_py_stack --no-index `
  find-links wheelhouse\wheels
```
