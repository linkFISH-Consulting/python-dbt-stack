# Updating Dependencies in this Repo

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
uv export --locked --no-hashes --no-emit-project -o requirements.txt
```

- Update changelog, and possibly version number in pyproject.toml

- Open PR

- Note: Dont forget to run `uv sync`, even after you only bumped our own version `pyproject.toml`.
