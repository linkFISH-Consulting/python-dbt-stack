"""Test selection via CLI `--select` argument"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_select_multiple_steps_batch() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        result = _run_example(tmp_path, ["step_a", "step_b"])

    stdout = result.stdout
    stderr = result.stderr

    assert result.returncode == 0, (
        f"Non-zero exit code.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )
    assert _has_line(stdout, "step_a", "PASS", "All good")
    assert _has_line(stdout, "step_b", "PASS", "Also all good")
    assert _has_line(stdout, "step_c", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout, "step_d", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout, "step_e", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout, "step_f", "OMIT", "Did not run (as requested via CLI)")


def test_select_range_from_to() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        result = _run_example(tmp_path, ["step_b...step_d"])

    stdout = result.stdout
    stderr = result.stderr

    assert result.returncode == 1, (
        f"Expected non-zero exit code (step_c FAILs).\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )
    assert _has_line(stdout, "step_a", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout, "step_b", "PASS", "Also all good")
    assert _has_line(stdout, "step_c", "FAIL", "Something went wrong")
    assert _has_line(stdout, "step_d", "SKIP", "Skipped due to failure in step_c")
    assert _has_line(stdout, "step_e", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout, "step_f", "OMIT", "Did not run (as requested via CLI)")


def test_select_with_arguments_passed_to_step() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        result = _run_example(tmp_path, ["step_a", "step_b: --foo bar"])

    stdout = result.stdout
    stderr = result.stderr

    assert result.returncode == 0, (
        f"Non-zero exit code.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )
    assert "Cli Arguments to this step: --foo bar" in stdout
    assert _has_line(stdout, "step_a", "PASS", "All good")
    assert _has_line(stdout, "step_b", "PASS", "Also all good")


def test_select_multiple_flags_union_with_arg_selected_step() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        result = _run_example(tmp_path, ["step_a", "step_d", "step_b: --x 1"])

    stdout = result.stdout
    stderr = result.stderr

    assert result.returncode == 0, (
        f"Non-zero exit code.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )
    assert "Cli Arguments to this step: --x 1" in stdout
    assert _has_line(stdout, "step_a", "PASS", "All good")
    assert _has_line(stdout, "step_b", "PASS", "Also all good")
    # step_d depends on step_c and executes step_c implicitly, so it passes.
    assert _has_line(stdout, "step_d", "PASS", "All good")


def test_select_from_start_and_to_end_shortcuts() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)

        from_start = _run_example(tmp_path, ["+step_c"])
        to_end = _run_example(tmp_path, ["step_d+"], ["--omit", "step_f"])

    stdout_a = from_start.stdout
    stdout_b = to_end.stdout

    # +step_c includes step_a, step_b, step_c — step_c FAILs → exit 1
    assert from_start.returncode == 1, (
        f"Expected non-zero exit code (step_c FAILs).\nSTDOUT:\n{from_start.stdout}\nSTDERR:\n{from_start.stderr}"
    )
    assert _has_line(stdout_a, "step_a", "PASS", "All good")
    assert _has_line(stdout_a, "step_b", "PASS", "Also all good")
    assert _has_line(stdout_a, "step_c", "FAIL", "Something went wrong")
    assert _has_line(stdout_a, "step_d", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout_a, "step_e", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout_a, "step_f", "OMIT", "Did not run (as requested via CLI)")

    # step_d+ includes step_d, step_e, (but wer skip step_f) — all PASS → exit 0
    assert to_end.returncode == 0, (
        f"Non-zero exit code.\nSTDOUT:\n{to_end.stdout}\nSTDERR:\n{to_end.stderr}"
    )
    assert _has_line(stdout_b, "step_a", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout_b, "step_b", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout_b, "step_c", "OMIT", "Did not run (as requested via CLI)")
    assert _has_line(stdout_b, "step_d", "PASS", "All good")
    assert _has_line(stdout_b, "step_e", "PASS")
    assert _has_line(stdout_b, "step_f", "OMIT", "Did not run (as requested via CLI)")


def _run_example(
    tmp_path: Path, step_args: list[str], other_args: list[str] = []
) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    example_script = repo_root / "src" / "lf_py_stack" / "orchestration" / "example.py"

    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("hello\n", encoding="utf-8")

    cmd = [sys.executable, str(example_script), "run"]
    for s in step_args:
        cmd.extend(["-s", s])

    cmd.extend(other_args)

    return subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        check=False,
    )


def _has_line(stdout: str, *parts: str) -> bool:
    lines = stdout.splitlines()
    return any(all(part in line for part in parts) for line in lines)
