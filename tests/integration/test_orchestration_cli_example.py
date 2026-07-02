"""Test the cli command we use for the docs."""

import os
import subprocess
import sys
from pathlib import Path


def test_cli_exit_code_0_on_passing_steps(tmp_path: Path) -> None:
    """Integration test that the CLI returns exit code 0 when all selected steps PASS.

    Writes a minimal pipeline module with two guaranteed-pass steps and runs it
    via ``cli run -s``, verifying returncode == 0.
    """
    repo_root = Path(__file__).resolve().parents[2]

    # Create a self-contained module with two trivially-passing steps.
    pipeline = tmp_path / "pipeline_pass.py"
    pipeline.write_text(
        """\
from lf_py_stack.orchestration import StepResult, cli_app

def clean_step_a() -> StepResult:
    return StepResult("PASS", "ok")

def clean_step_b(clean_step_a: StepResult) -> StepResult:
    return StepResult("PASS", "also ok")

if __name__ == "__main__":
    cli_app()
""",
        encoding="utf-8",
    )

    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, str(pipeline), "run", "-s", "clean_step_a", "-s", "clean_step_b"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    stdout = result.stdout
    stderr = result.stderr
    assert result.returncode == 0, (
        f"Expected exit code 0 for all-pass run.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )
    assert "clean_step_a" in stdout
    assert "clean_step_b" in stdout
    assert "Orchestration run complete" in stdout


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

    # step_c FAILs in this example → exit 1
    assert result.returncode == 1, f"Expected non-zero exit code (step_c FAILs).\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

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
