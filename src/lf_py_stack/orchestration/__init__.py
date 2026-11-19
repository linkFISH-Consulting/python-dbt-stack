"""Deprecated shim: the orchestration tooling moved to its own repository.

This module only exists so that existing code using
``from lf_py_stack.orchestration import ...`` keeps working. It re-exports the
public API of the standalone ``lf-orchestrator`` package and emits a
``DeprecationWarning`` on import.

The real implementation lives at
https://github.com/linkFISH-Consulting/lf_orchestrator
"""

import sys
import warnings
from importlib import import_module
from types import FrameType
from typing import Any

NEW_REPO_URL = "https://github.com/linkFISH-Consulting/lf_orchestrator"

DEPRECATION_MESSAGE = f"""\
`lf_py_stack.orchestration` is deprecated and will be removed in a future release.
The orchestration tooling now lives in its own repository:
  {NEW_REPO_URL}

Confirm that the new package is installed:
  uv pip show lf-orchestrator

And change your import from
  from lf_py_stack.orchestration import cli_app
to
  from lf_orchestrator import cli_app
"""


def _warning_context() -> tuple[str, dict[str, Any]]:
    """Return the importing module and its warning registry."""
    frame: FrameType | None = sys._getframe(1)
    while frame is not None:
        module = frame.f_globals.get("__name__", "")
        if module != __name__ and not module.startswith(
            ("importlib.", "_frozen_importlib")
        ):
            return module, frame.f_globals
        frame = frame.f_back
    return __name__, globals()


# A synthetic filename prevents Python from appending the import-site source
# line to this multi-line message. Use the importer's module for warning
# filtering, preserving the usual behavior (visible in __main__, ignored in
# most imported modules unless warnings are enabled).
_warning_module, _warning_globals = _warning_context()
warnings.warn_explicit(
    DEPRECATION_MESSAGE,
    DeprecationWarning,
    filename=__name__,
    lineno=1,
    module=_warning_module,
    registry=_warning_globals.setdefault("__warningregistry__", {}),
)
del _warning_context, _warning_module, _warning_globals

try:
    from lf_orchestrator import (
        StepResult,
        cli_app,
        config,
        get_dbt_versions,
        get_logger,
        log_dbt_versions,
        log_step_nodes_table,
        log_step_results_table,
        mail_app,
        run_cli_command,
        send_mail,
        shrink_duckdb,
        truncate,
    )
except ImportError as exc:  # pragma: no cover - only when the new package is missing
    raise ImportError(
        "`lf_py_stack.orchestration` is a deprecated shim and requires the "
        "`lf-orchestrator` package. Install it with:\n"
        f'  uv add "git+{NEW_REPO_URL}.git@main"\n'
        f"Original error: {exc}"
    ) from exc

# Import the submodules that the original package imported eagerly, so that
# `lf_py_stack.orchestration.<module>` attribute access keeps working without an
# explicit import. `import_module` is used instead of `from . import ...`
# because attribute lookups on this package can be shadowed by the re-exports
# above (see the `config` case below).
for _submodule in ("cli", "components", "duckdb", "logger", "mail", "steps"):
    import_module(f"{__name__}.{_submodule}")
del _submodule

# `config` is special: importing the submodule rebinds the attribute `config` on
# this package to the module, so we import it and then restore the instance.
# This keeps `from lf_py_stack.orchestration import config` returning the
# `OrchestrationConfig` object, as it did before the split.
_config_shim = import_module(f"{__name__}.config")

config = _config_shim.config

__all__ = [
    "StepResult",
    "log_step_nodes_table",
    "log_step_results_table",
    "log_dbt_versions",
    "get_dbt_versions",
    "run_cli_command",
    "get_logger",
    "send_mail",
    "shrink_duckdb",
    "truncate",
    "mail_app",
    "cli_app",
    "config",
]
