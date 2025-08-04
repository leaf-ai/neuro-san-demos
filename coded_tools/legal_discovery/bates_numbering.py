"""Bates numbering and PDF stamping utilities.

This module provides a small, self-contained Bates numbering service
backed by SQLite via SQLAlchemy.  It also exposes a helper for stamping
PDF files with Bates numbers using PyMuPDF (``fitz``).
"""

from __future__ import annotations

from typing import Tuple

import fitz  # PyMuPDF
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import Session, declarative_base


Base = declarative_base()


class BatesCounter(Base):
    """SQLAlchemy model storing the current Bates counter for a prefix."""

    __tablename__ = "bates_counter"

    id = Column(Integer, primary_key=True)
    prefix = Column(String, nullable=False, default="BATES")
    current_number = Column(Integer, nullable=False, default=0)


class BatesNumberingService:
    """Service that generates sequential Bates numbers.

    Parameters
    ----------
    db_url: str, optional
        Database URL used by SQLAlchemy.  Defaults to an in-memory SQLite
        database which is sufficient for testing and light-weight use.
    """

    def __init__(self, db_url: str = "sqlite+pysqlite:///:memory:") -> None:
        self.engine = create_engine(db_url, future=True)
        # Create the table on first use
        Base.metadata.create_all(self.engine)

    def get_next_bates_number(self, prefix: str = "ABCD") -> str:
        """Atomically fetch the next Bates number for *prefix*.

        If ``prefix`` is new it will be initialised starting at 1.
        """

        with Session(self.engine) as session, session.begin():
            row = session.execute(
                text(
                    "UPDATE bates_counter SET current_number = current_number + 1 "
                    "WHERE prefix = :p RETURNING current_number"
                ),
                {"p": prefix},
            ).fetchone()
            if row is None:
                # No row for this prefix yet; insert starting at 1.
                session.execute(
                    text(
                        "INSERT INTO bates_counter (prefix, current_number) "
                        "VALUES (:p, 1)"
                    ),
                    {"p": prefix},
                )
                number = 1
            else:
                number = row.current_number
        return f"{prefix}_{number:06d}"


def stamp_pdf(
    file_path: str, output_path: str, start_number: int, prefix: str = "ABCD"
) -> Tuple[str, str]:
    """Stamp *file_path* with sequential Bates numbers.

    Parameters
    ----------
    file_path: str
        Path to the input PDF.
    output_path: str
        Path where the stamped PDF will be written.
    start_number: int
        First Bates number to use for stamping.
    prefix: str
        Bates prefix to apply.  Default ``"ABCD"``.

    Returns
    -------
    Tuple[str, str]
        The start and end Bates numbers applied to the document.
    """

    doc = fitz.open(file_path)
    for i, page in enumerate(doc, start=start_number):
        stamp = f"{prefix}_{i:06d}"
        page.insert_text((50, 20), stamp, fontsize=8, color=(0, 0, 0), overlay=True)
    doc.save(output_path)
    end_number = start_number + len(doc) - 1
    return f"{prefix}_{start_number:06d}", f"{prefix}_{end_number:06d}"


__all__ = ["BatesNumberingService", "stamp_pdf"]
