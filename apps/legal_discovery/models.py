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
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    dependencies = db.relationship('TaskDependency', foreign_keys='TaskDependency.task_id', backref='task', lazy=True)

class TaskDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    depends_on_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    bates_number = db.Column(db.String(100), nullable=True)
    privilege_status = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class KnowledgeGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    entity1 = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(100), nullable=False)
    entity2 = db.Column(db.String(100), nullable=False)

class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class QAReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class UserSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # In a real app, this would be a foreign key to a users table
    courtlistener_api_key = db.Column(db.String(255), nullable=True)
    gemini_api_key = db.Column(db.String(255), nullable=True)
    california_codes_url = db.Column(db.String(255), nullable=True)

class FileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, server_default=db.func.now())

class ForensicAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    analysis_type = db.Column(db.String(100), nullable=False) # e.g., 'Authentication', 'Financial'
    findings = db.Column(db.Text, nullable=True)
    analyst_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class LegalReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    citation = db.Column(db.String(255), nullable=False)
    source_url = db.Column(db.String(255), nullable=True)
    retrieved_at = db.Column(db.DateTime, server_default=db.func.now())

class TimelineExport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Additional tables for a total of 17
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)

class LegalTheory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    theory_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Deposition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    deponent_name = db.Column(db.String(255), nullable=False)
    deposition_date = db.Column(db.DateTime, nullable=False)
    transcript_path = db.Column(db.String(255), nullable=True)
