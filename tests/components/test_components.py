from pathlib import Path

from lf_py_stack.orchestration.components import log_dbt_versions, run_cli_command


def test_run_cli_command_captures_output_without_printing() -> None:
    code, output = run_cli_command(
        "printf 'hello\\nworld\\n'",
        print_to_stdout=False,
    )

    assert code == 0
    assert output == "hello\nworld\n"


def test_run_cli_command_nonzero_exit_code() -> None:
    code, output = run_cli_command("echo boom && exit 7", print_to_stdout=False)

    assert code == 7
    assert "boom" in output


def test_log_dbt_versions_minimal_with_mocked_yaml_files(tmp_path: Path) -> None:
    # dbt_project.yml
    (tmp_path / "dbt_project.yml").write_text(
        """
name: my_dbt_project
version: 1.2.3
""".strip()
        + "\n",
        encoding="utf-8",
    )

    # packages.yml (includes package+version and git+revision forms)
    (tmp_path / "packages.yml").write_text(
        """
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - git: https://github.com/dbt-labs/dbt-date
    revision: 0.10.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    # package-lock.yml supplements package versions/revisions
    (tmp_path / "package-lock.yml").write_text(
        """
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - package: calogica/dbt_expectations
    version: 0.10.4
""".strip()
        + "\n",
        encoding="utf-8",
    )

    out = log_dbt_versions(
        dbt_project_dir=tmp_path,
        return_format="minimal",
        show_source_file=True,
    )

    assert "my_dbt_project 1.2.3 (via dbt_project.yml)" in out
    assert "dbt-labs/dbt_utils 1.1.1 (via packages.yml)" in out
    assert "https://github.com/dbt-labs/dbt-date 0.10.0 (via packages.yml)" in out
    assert "calogica/dbt_expectations 0.10.4 (via package-lock.yml)" in out
