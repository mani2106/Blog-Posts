# Compatibility shim to satisfy nbdev v0.2.x imports that expect fastscript.Param
# Place this file at the repository root. It is intentionally minimal — extend it
# if nbdev or other tools require more symbols later.

from dataclasses import dataclass
from typing import Any, Callable, Optional, Iterable

@dataclass
class Param:
    "Minimal stand-in for the fastscript.Param used by nbdev v0.2"
    default: Any = None
    help: str = ""
    nargs: Optional[Any] = None

    def __repr__(self):
        return f"Param(default={self.default!r}, help={self.help!r}, nargs={self.nargs!r})"

def call_parse(func: Optional[Callable] = None, **kwargs):
    """
    No-op decorator that preserves the function. Old nbdev/fastscript sometimes
    uses call_parse only to decorate notebook/CLI functions; we don't need the CLI
    behavior for export2html, so a noop is fine.
    """
    if func is None:
        def _inner(f: Callable) -> Callable:
            return f
        return _inner
    return func

# Provide additional small helpers that older code sometimes imports
def store_args(*_args, **_kwargs):
    "No-op compatibility function for store_args-style imports"
    def _inner(f):
        return f
    return _inner

# Export expected symbols
__all__ = ["Param", "call_parse", "store_args"]