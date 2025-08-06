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
    weasyprint = types.ModuleType("weasyprint")

    class HTML:  # type: ignore
        """Minimal stand-in for :class:`weasyprint.HTML`."""

        def __init__(self, string: str | None = None, *_, **__):
            self.string = string

        def write_pdf(self, target: str, *_args, **_kwargs) -> None:
            """Create a tiny PDF so tests can confirm file output."""
            with open(target, "wb") as fh:
                fh.write(b"%PDF-1.4\n%stub")

    weasyprint.HTML = HTML
    sys.modules["weasyprint"] = weasyprint
