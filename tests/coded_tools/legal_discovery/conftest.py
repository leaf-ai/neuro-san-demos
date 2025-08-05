import sys
import types
import pathlib

# Ensure repository root on path
ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub package to avoid heavy imports in coded_tools.legal_discovery.__init__
package_path = ROOT / "coded_tools" / "legal_discovery"
pkg = types.ModuleType("coded_tools.legal_discovery")
pkg.__path__ = [str(package_path)]
sys.modules.setdefault("coded_tools.legal_discovery", pkg)

# Skip tests requiring optional heavy dependencies
import importlib.util
collect_ignore = []
if importlib.util.find_spec("weasyprint") is None:
    collect_ignore.append("test_deposition_prep.py")
