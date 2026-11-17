"""Helper for the deprecated orchestration submodule shims.

Each submodule of ``lf_py_stack.orchestration`` forwards attribute access to
the corresponding module in the standalone ``lf_orchestrator`` package. The
deprecation warning itself is emitted once, when the package ``__init__`` runs.
"""

from collections.abc import Callable
from types import ModuleType
from typing import Any

NEW_REPO_URL = "https://github.com/linkFISH-Consulting/lf_orchestrator"


def module_getattr(module: ModuleType, new_module: str) -> Callable[[str], Any]:
    """Build a PEP 562 module ``__getattr__`` forwarding to ``module``.

    Args:
        module: The ``lf_orchestrator`` module to delegate to.
        new_module: The import path of ``module``, used in error messages.
    """

    def _getattr(name: str) -> Any:
        # Never forward dunder lookups: it confuses import machinery and
        # introspection tools, and the new module has nothing to offer there.
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        try:
            return getattr(module, name)
        except AttributeError:
            raise AttributeError(
                f"module {new_module!r} has no attribute {name!r}"
            ) from None

    # The shim modules assign this to their module-level `__getattr__` (PEP 562).
    return _getattr


def module_dir(module: ModuleType) -> Callable[[], list[str]]:
    """Build a module ``__dir__`` listing the delegated module's contents."""

    def _dir() -> list[str]:
        return sorted(set(dir(module)))

    # Assigned to the module-level `__dir__` by the shim modules.
    return _dir
