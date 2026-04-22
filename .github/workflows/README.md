# Workflows

## Wheelhouse creation

To deploy:

```bat
uv venv --python portable\python\python.exe .venv

uv pip sync wheelhouse\requirements.txt ^
  --python .venv\Scripts\python.exe ^
  --no-index ^
  --find-links wheelhouse\wheels
```
