"""The orchestration tooling moved to `lf_orchestrator`.

`lf_py_stack.orchestration` is kept as a backward compatible shim. These tests
pin the two promises we make to existing users: importing it warns and points
to the new repository, and the public API is still reachable.
"""

import importlib
import warnings

import pytest

import lf_py_stack.orchestration as orchestration


def _deprecation_messages() -> list[str]:
    """Reload the package and return the deprecation warnings it emitted."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(orchestration)
    return [
        str(warning.message)
        for warning in caught
        if issubclass(warning.category, DeprecationWarning)
    ]


def test_import_emits_deprecation_warning():
    messages = _deprecation_messages()

    assert messages, "importing the shim must emit a DeprecationWarning"
    message = messages[0]
    assert "https://github.com/linkFISH-Consulting/lf_orchestrator" in message
    # Tell users how to check the installation and how to import instead.
    assert "uv pip show lf-orchestrator" in message
    assert "from lf_orchestrator import cli_app" in message


def test_public_api_is_reexported():
    import lf_orchestrator

    for name in orchestration.__all__:
        assert getattr(orchestration, name) is getattr(lf_orchestrator, name)


def test_submodules_delegate_to_new_package():
    from lf_orchestrator.components import run_cli_command
    from lf_orchestrator.duckdb import shrink_duckdb
    from lf_orchestrator.steps import StepResult

    from lf_py_stack.orchestration.components import run_cli_command as shimmed_command
    from lf_py_stack.orchestration.duckdb import shrink_duckdb as shimmed_shrink
    from lf_py_stack.orchestration.steps import StepResult as shimmed_result

    assert shimmed_command is run_cli_command
    assert shimmed_shrink is shrink_duckdb
    assert shimmed_result is StepResult


def test_unknown_attributes_raise_attribute_error():
    with pytest.raises(AttributeError):
        _ = orchestration.does_not_exist  # type: ignore[attr-defined]
