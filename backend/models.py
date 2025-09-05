from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Workspace(db.Model):
    __tablename__ = "workspace"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title= db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    
    uploaded_files = db.relationship("UploadedFile", backref="workspace", lazy=True)

class UploadedFile(db.Model):
    __tablename__ = "uploaded_file"
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspace.id"), nullable=False)
    filename = db.Column(db.String(512), nullable=False)
    path = db.Column(db.String(1024), nullable=False)
    summary = db.Column(db.Text)
    study_plan = db.Column(db.Text)
    videos = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chunks = db.relationship("DocChunk", backref="file", lazy=True)
    
    def to_dict(self):
        import json
        def _loads(s, default):
            if not s: 
                return default
            try:
                return json.loads(s)
            except Exception:
                # if it was stored as plain string accidentally
                return default if default is not None else s

        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "filename": self.filename,
            "summary": self.summary or "",
            "study_plan": _loads(self.study_plan, {}),
            "videos": _loads(self.videos, []),
            "created_at": self.created_at.isoformat() + "Z",
        }

class DocChunk(db.Model):
    __tablename__ = "doc_chunk"
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("uploaded_file.id"), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspace.id"), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    start_pos = db.Column(db.Integer)
    end_pos = db.Column(db.Integer)
    token_count = db.Column(db.Integer)
    embedding = db.Column(JSON)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))