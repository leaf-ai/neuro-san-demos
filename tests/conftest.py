import importlib
import sys
import pytest

for name in (
    "langchain_google_genai",
    "coded_tools.legal_discovery.privilege_detector",
):
    if name in sys.modules:
        del sys.modules[name]
    try:
        importlib.import_module(name)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def restore_stubs():
    for name in (
        "langchain_google_genai",
        "coded_tools.legal_discovery.privilege_detector",
    ):
        if name in sys.modules:
            del sys.modules[name]
        importlib.import_module(name)
    yield
