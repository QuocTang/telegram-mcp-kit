"""Auto-discovery for tool modules."""

import importlib
import pkgutil
from pathlib import Path


def discover_tools():
    """Import all tool modules in this package (skipping _private ones).

    Any module in ``tools/`` that does not start with ``_`` will be imported,
    which causes its ``@mcp.tool()`` decorators to register with the shared
    ``mcp`` instance from ``_base``.
    """
    package_dir = str(Path(__file__).parent)
    for module_info in pkgutil.iter_modules([package_dir]):
        if not module_info.name.startswith("_"):
            importlib.import_module(f"telegram_mcp_kit.tools.{module_info.name}")
