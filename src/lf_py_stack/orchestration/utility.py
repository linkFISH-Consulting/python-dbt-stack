"""Deprecated shim: use ``lf_orchestrator.utility`` instead.

Kept only for backward compatibility. The implementation moved to
https://github.com/linkFISH-Consulting/lf_orchestrator
"""

from importlib import import_module

from lf_py_stack.orchestration._shim import module_dir, module_getattr

# `import_module` rather than `import lf_orchestrator.utility as _module`: some
# submodule names are shadowed by same-named attributes on the new package
# (e.g. `config`), and attribute access would hand us the wrong object.
_module = import_module("lf_orchestrator.utility")

__getattr__ = module_getattr(_module, "lf_orchestrator.utility")
__dir__ = module_dir(_module)
