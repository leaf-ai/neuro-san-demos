from .database import db


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


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    bates_number = db.Column(db.String(100), nullable=True)
    privilege_status = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    content_hash = db.Column(db.String(64), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    metadata_entries = db.relationship(
        "DocumentMetadata",
        backref="document",
        lazy=True,
        cascade="all, delete-orphan",
    )


class DocumentMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    schema = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=False)


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
    elements = db.relationship(
        "Element", backref="cause", lazy=True, cascade="all, delete-orphan"
    )
    defenses = db.relationship(
        "Defense", backref="cause", lazy=True, cascade="all, delete-orphan"
    )


class Element(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cause_id = db.Column(
        db.Integer, db.ForeignKey("cause_of_action.id"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)


class Defense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cause_id = db.Column(
        db.Integer, db.ForeignKey("cause_of_action.id"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)


class Fact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    document_id = db.Column(
        db.Integer, db.ForeignKey("document.id"), nullable=False
    )
    legal_theory_id = db.Column(
        db.Integer, db.ForeignKey("legal_theory.id"), nullable=True
    )
    element_id = db.Column(db.Integer, db.ForeignKey("element.id"), nullable=True)
    text = db.Column(db.Text, nullable=False)
    parties = db.Column(db.JSON, nullable=True)
    dates = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    document = db.relationship("Document", backref=db.backref("facts", lazy=True))
    legal_theory = db.relationship(
        "LegalTheory", backref=db.backref("facts", lazy=True)
    )
    element = db.relationship("Element", backref=db.backref("facts", lazy=True))
