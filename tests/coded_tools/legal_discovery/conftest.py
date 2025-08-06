import sys
import types
import pathlib
import importlib.util

# Ensure repository root on path
ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub package to avoid heavy imports in coded_tools.legal_discovery.__init__
package_path = ROOT / "coded_tools" / "legal_discovery"
pkg = types.ModuleType("coded_tools.legal_discovery")
pkg.__path__ = [str(package_path)]
sys.modules.setdefault("coded_tools.legal_discovery", pkg)

# Provide a lightweight stub for weasyprint if it's not installed
if importlib.util.find_spec("weasyprint") is None:  # pragma: no cover - environment specific
    from tests.stubs import weasyprint as weasyprint_stub

    sys.modules.setdefault("weasyprint", weasyprint_stub)

# Stub google generative AI SDK if unavailable
try:  # pragma: no cover - environment specific
    importlib.util.find_spec("google.generativeai")
except ModuleNotFoundError:
    google_pkg = types.ModuleType("google")
    sys.modules.setdefault("google", google_pkg)
    sys.modules.setdefault("google.generativeai", types.ModuleType("google.generativeai"))
