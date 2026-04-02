# Deploying with Conda

We keep the requirements.txt up to date with _locked_ Versions of all packages,
so you can simply include it in your Conda environment.

We have a specific URL for each release. By pinning to that version, you will also pin dependencies.
In the example below we pinned to version `v0.1.5`

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
    - -r https://raw.githubusercontent.com/linkFISH-Consulting/python-dbt-stack/refs/tags/v0.1.5/requirements.txt
```

To get the latest version from the main branch (without pinning, and not necessarily matching a release):

```yaml
  - pip:
    - -r https://raw.githubusercontent.com/linkFISH-Consulting/python-dbt-stack/main/requirements.txt
```
