from .database import db
import enum
import uuid
from sqlalchemy import event


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    capabilities = db.Column(db.Text, nullable=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("agent.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    dependencies = db.relationship("TaskDependency", foreign_keys="TaskDependency.task_id", backref="task", lazy=True)


class TaskDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    depends_on_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)


class MessageVisibility(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    ATTORNEY_ONLY = "attorney_only"


class Conversation(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=True)
    participants = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    vector_id = db.Column(db.String(255), nullable=True)
    messages = db.relationship(
        "Message", backref="conversation", lazy=True, cascade="all, delete-orphan"
    )


class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(
        db.String(36), db.ForeignKey("conversation.id"), nullable=False, index=True
    )
    sender_id = db.Column(db.Integer, db.ForeignKey("agent.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    document_ids = db.Column(db.JSON, nullable=True)
    reply_to_id = db.Column(db.String(36), db.ForeignKey("message.id"), nullable=True)
    visibility = db.Column(
        db.Enum(MessageVisibility), nullable=False, default=MessageVisibility.PUBLIC
    )
    vector_id = db.Column(db.String(255), nullable=True)

    sender = db.relationship("Agent", backref=db.backref("messages", lazy=True))
    reply_to = db.relationship("Message", remote_side=[id])


class MessageAuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(36), db.ForeignKey("message.id"), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    transcript = db.Column(db.Text, nullable=False)
    voice_model = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    message = db.relationship("Message", backref=db.backref("audit_logs", lazy=True))


class DocumentSource(enum.Enum):
    USER = "user"
    OPP_COUNSEL = "opp_counsel"
    COURT = "court"


class ChainEventType(enum.Enum):
    INGESTED = "INGESTED"
    HASHED = "HASHED"
    REDACTED = "REDACTED"
    STAMPED = "STAMPED"
    VERSIONED = "VERSIONED"
    DELETED = "DELETED"
    EXPORTED = "EXPORTED"
    ACCESSED = "ACCESSED"


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    bates_number = db.Column(db.String(100), nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    sha256 = db.Column(db.String(64), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    source = db.Column(db.Enum(DocumentSource), nullable=False, default=DocumentSource.USER)
    is_privileged = db.Column(db.Boolean, nullable=False, default=False)
    is_redacted = db.Column(db.Boolean, nullable=False, default=False)
    needs_review = db.Column(db.Boolean, nullable=False, default=False)
    is_exhibit = db.Column(db.Boolean, nullable=False, default=False)
    exhibit_number = db.Column(db.String(50), unique=True)
    exhibit_title = db.Column(db.String(255))
    exhibit_order = db.Column(db.Integer, nullable=False, default=0)
    metadata_entries = db.relationship(
        "DocumentMetadata",
        backref="document",
        lazy=True,
        cascade="all, delete-orphan",
    )
    redaction_logs = db.relationship(
        "RedactionLog",
        backref="document",
        lazy=True,
        cascade="all, delete-orphan",
    )
    redaction_audits = db.relationship(
        "RedactionAudit",
        backref="document",
        lazy=True,
        cascade="all, delete-orphan",
    )
    witnesses = db.relationship(
        "Witness",
        secondary="document_witness_link",
        backref=db.backref("documents", lazy=True),
    )
    chain_logs = db.relationship(
        "ChainOfCustodyLog",
        backref="document",
        lazy=True,
        cascade="all, delete-orphan",
    )


class ChainOfCustodyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    event_type = db.Column(db.Enum(ChainEventType), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("agent.id"), nullable=True)
    source_team = db.Column(db.String(100), nullable=False, default="unknown")
    event_metadata = db.Column(db.JSON, nullable=True)

    user = db.relationship("Agent", backref=db.backref("chain_logs", lazy=True))


@event.listens_for(ChainOfCustodyLog, "before_update")
@event.listens_for(ChainOfCustodyLog, "before_delete")
def _prevent_chain_modification(*args, **kwargs):
    raise ValueError("Chain of custody logs are immutable")


class ExhibitCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False, unique=True)
    next_num = db.Column(db.Integer, nullable=False, default=1)


class ExhibitAuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=True)
    user = db.Column(db.String(255), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    details = db.Column(db.JSON, nullable=True)


class DocumentMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    schema = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=False)


class RedactionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(255), nullable=True)


class RedactionAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    reviewer = db.Column(db.String(255), nullable=True)
    action = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    reason = db.Column(db.Text, nullable=True)


class Witness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=True)
    associated_case = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=True)
    linked_user_id = db.Column(db.Integer, nullable=True)


class DocumentWitnessLink(db.Model):
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), primary_key=True)
    witness_id = db.Column(db.Integer, db.ForeignKey("witness.id"), primary_key=True)


class KnowledgeGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    entity1 = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(100), nullable=False)
    entity2 = db.Column(db.String(100), nullable=False)


class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class QAReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("agent.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class UserSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # In a real app, this would be a foreign key to a users table
    courtlistener_api_key = db.Column(db.String(255), nullable=True)
    gemini_api_key = db.Column(db.String(255), nullable=True)
    california_codes_url = db.Column(db.String(255), nullable=True)
    courtlistener_com_api_endpoint = db.Column(db.String(255), nullable=True)
    google_api_endpoint = db.Column(db.String(255), nullable=True)
    verifypdf_api_key = db.Column(db.String(255), nullable=True)
    verify_pdf_endpoint = db.Column(db.String(255), nullable=True)
    riza_key = db.Column(db.String(255), nullable=True)
    neo4j_uri = db.Column(db.String(255), nullable=True)
    neo4j_username = db.Column(db.String(255), nullable=True)
    neo4j_password = db.Column(db.String(255), nullable=True)
    neo4j_database = db.Column(db.String(255), nullable=True)
    aura_instance_id = db.Column(db.String(255), nullable=True)
    aura_instance_name = db.Column(db.String(255), nullable=True)
    gcp_project_id = db.Column(db.String(255), nullable=True)
    gcp_vertex_ai_data_store_id = db.Column(db.String(255), nullable=True)
    gcp_vertex_ai_search_app = db.Column(db.String(255), nullable=True)
    gcp_service_account_key = db.Column(db.Text, nullable=True)


class FileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, server_default=db.func.now())


class ForensicAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    analysis_type = db.Column(db.String(100), nullable=False)  # e.g., 'Authentication', 'Financial'
    findings = db.Column(db.Text, nullable=True)
    analyst_id = db.Column(db.Integer, db.ForeignKey("agent.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class LegalReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    citation = db.Column(db.String(255), nullable=False)
    source_url = db.Column(db.String(255), nullable=True)
    retrieved_at = db.Column(db.DateTime, server_default=db.func.now())


class TimelineExport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# Additional tables for a total of 17
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    description = db.Column(db.Text, nullable=True)


class LegalTheory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    theory_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    review_comment = db.Column(db.Text, nullable=True)


class Deposition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    deponent_name = db.Column(db.String(255), nullable=False)
    deposition_date = db.Column(db.DateTime, nullable=False)
    transcript_path = db.Column(db.String(255), nullable=True)


class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class CauseOfAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    elements = db.relationship("Element", backref="cause", lazy=True, cascade="all, delete-orphan")
    defenses = db.relationship("Defense", backref="cause", lazy=True, cascade="all, delete-orphan")


class Element(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cause_id = db.Column(db.Integer, db.ForeignKey("cause_of_action.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)


class Defense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cause_id = db.Column(db.Integer, db.ForeignKey("cause_of_action.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)


class Fact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    legal_theory_id = db.Column(db.Integer, db.ForeignKey("legal_theory.id"), nullable=True)
    element_id = db.Column(db.Integer, db.ForeignKey("element.id"), nullable=True, index=True)
    text = db.Column(db.Text, nullable=False)
    parties = db.Column(db.JSON, nullable=True)
    dates = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    witness_id = db.Column(db.Integer, db.ForeignKey("witness.id"), nullable=True)

    document = db.relationship("Document", backref=db.backref("facts", lazy=True))
    legal_theory = db.relationship("LegalTheory", backref=db.backref("facts", lazy=True))
    element = db.relationship("Element", backref=db.backref("facts", lazy=True))
    witness = db.relationship("Witness", backref=db.backref("facts", lazy=True))


class TheoryConfidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legal_theory_id = db.Column(db.Integer, db.ForeignKey("legal_theory.id"), nullable=False)
    fact_id = db.Column(db.Integer, db.ForeignKey("fact.id"), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    source_team = db.Column(db.String(100), nullable=False, default="unknown")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (
        db.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_theory_confidence_range"),
    )

    legal_theory = db.relationship(
        "LegalTheory",
        backref=db.backref("confidence_links", lazy=True, cascade="all, delete-orphan"),
    )
    fact = db.relationship(
        "Fact",
        backref=db.backref("theory_links", lazy=True, cascade="all, delete-orphan"),
    )


class DepositionQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    witness_id = db.Column(db.Integer, db.ForeignKey("witness.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    question = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(255), nullable=True)
    flagged = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    witness = db.relationship("Witness", backref=db.backref("questions", lazy=True))


class DepositionReviewLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("agent.id"), nullable=False)
    witness_id = db.Column(db.Integer, db.ForeignKey("witness.id"), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    approved = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)

    witness = db.relationship("Witness", backref=db.backref("reviews", lazy=True))
    reviewer = db.relationship("Agent", backref=db.backref("deposition_reviews", lazy=True))


class FactConflict(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    witness_id = db.Column(db.Integer, db.ForeignKey("witness.id"), nullable=False)
    fact1_id = db.Column(db.Integer, db.ForeignKey("fact.id"), nullable=False)
    fact2_id = db.Column(db.Integer, db.ForeignKey("fact.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    fact1 = db.relationship("Fact", foreign_keys=[fact1_id])
    fact2 = db.relationship("Fact", foreign_keys=[fact2_id])
    witness = db.relationship("Witness", backref=db.backref("conflicts", lazy=True))
