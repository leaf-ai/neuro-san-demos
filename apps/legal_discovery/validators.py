"""Input validation schemas for Legal Discovery endpoints."""

from pydantic import BaseModel


class ExhibitAssignPayload(BaseModel):
    """Schema for assigning an exhibit number to a document."""

    document_id: int
    title: str | None = None
    user: str | None = None


class NarrativeDiscrepancyAnalyzePayload(BaseModel):
    """Schema for analyzing narrative discrepancies in a document."""

    opposing_doc_id: int
