"""Minimal stub of :mod:`weasyprint` for unit tests.

The real `weasyprint` package is heavy and may not be installed in
lightweight environments.  This stub provides a tiny subset sufficient for
our tests: the :class:`HTML` class with a :meth:`write_pdf` method that
emits a minimal PDF header so the resulting file is non-empty.
"""

class HTML:  # pragma: no cover - trivial
    """Stand-in for :class:`weasyprint.HTML`."""

    def __init__(self, string: str | None = None, *_, **__):
        self.string = string

    def write_pdf(self, target: str, *_args, **_kwargs) -> None:
        with open(target, "wb") as fh:
            fh.write(b"%PDF-1.4\n%stub")
