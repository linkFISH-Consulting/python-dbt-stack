"""Test the cli command we use for the docs."""

import os
import subprocess
import sys
from pathlib import Path


def test_example_run_all_omit_step_f(tmp_path: Path) -> None:
    """Integration test for example orchestration flow.

    Runs:
        python ./src/lf_py_stack/orchestration/example.py run -s all -o step_f

    Asserts exit code and key output fragments loosely.
    """
    repo_root = Path(__file__).resolve().parents[2]
    example_script = repo_root / "src" / "lf_py_stack" / "orchestration" / "example.py"

    # Keep ls output deterministic-ish by running from an isolated temp dir
    # with one known file.
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("hello\n", encoding="utf-8")

    env = os.environ.copy()

    result = subprocess.run(
        [
            sys.executable,
            str(example_script),
            "run",
            "-s",
            "all",
            "-s",
            "step_b:hello world",
            # subprocess does not use shell parsing, so dont add quotes!
            "-o",
            "step_f",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    stdout = result.stdout
    stderr = result.stderr

    assert result.returncode == 0, f"Non-zero exit code.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

    # High-level flow
    assert "Running the following steps:" in stdout
    assert "Orchestration run complete" in stdout

    # Step execution messages.
    # step_d/e use logger output; those lines may not be printed to stdout.
    assert "Hello from step_a" in stdout
    assert "Hello from step_b" in stdout
    assert "Hello from step_c" in stdout

    # step_b contextual output (shell value itself may vary)
    assert "Current shell:" in stdout
    assert "Cli Arguments to this step: hello world" in stdout
    assert "Previous step result: All good" in stdout

    # Expected summary table rows (line-by-line, loose on spacing)
    lines = stdout.splitlines()

    def has_line(*parts: str) -> bool:
        return any(all(part in line for part in parts) for line in lines)

    assert has_line("step_a", "PASS", "All good")
    assert has_line("step_b", "PASS", "Also all good")
    assert has_line("step_c", "FAIL", "Something went wrong")
    assert has_line("step_d", "SKIP", "Skipped due to failure in step_c")
    assert has_line("step_e", "PASS")
    assert has_line("step_f", "OMIT", "Did not run (as requested via CLI)")

    # step_e logs output from `ls -l`.
    assert "dummy.txt" in stdout
