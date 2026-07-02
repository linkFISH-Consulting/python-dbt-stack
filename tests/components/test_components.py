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


def test_run_cli_command_handles_invalid_utf8_bytes(tmp_path: Path) -> None:
    """Ensure run_cli_command survives subprocess output containing invalid UTF-8.

    On Windows the system console encoding (e.g. GBK, CP1252) can produce byte
    sequences that are not valid UTF-8.  Without ``errors="replace"`` the
    subprocess pipe would raise a UnicodeDecodeError and crash the run.

    We write a small script that spits out raw invalid-UTF-8 bytes via stdout
    and verify that run_cli_command completes without raising.
    """
    # A script that writes known-invalid-UTF-8 bytes to stdout's buffer.
    # \xff\xfe are never valid in UTF-8, \xc0\x80 is an overlong encoding,
    # and \x80 is a standalone continuation byte.
    bad_script = tmp_path / "bad_output.py"
    bad_script.write_bytes(
        b"import sys\n"
        b"sys.stdout.buffer.write(b'hello ')\n"
        b"sys.stdout.buffer.write(b'\\xff\\xfe\\xc0\\x80\\x80')\n"
        b"sys.stdout.buffer.write(b' world\\n')\n"
    )

    code, output = run_cli_command(
        f"python {bad_script}",
        print_to_stdout=False,
    )

    assert code == 0
    assert "hello" in output
    assert "world" in output


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
        show_source_file=True,
    )

    assert "my_dbt_project 1.2.3 (via dbt_project.yml)" in out
    assert "dbt-labs/dbt_utils 1.1.1 (via packages.yml)" in out
    assert "https://github.com/dbt-labs/dbt-date 0.10.0 (via packages.yml)" in out
    assert "calogica/dbt_expectations 0.10.4 (via package-lock.yml)" in out
