# backend/uploads.py
import json
import os
import fitz
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db,Workspace, UploadedFile, DocChunk
from services.llm_service import generate_study_package, embed_text

uploads_bp = Blueprint("uploads_bp", __name__, url_prefix="/api/uploads")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split text into overlapping chunks of roughly `chunk_size` characters.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append((chunk, start, end))
        start = end - overlap  # overlap for context
        if start < 0:
            start = 0
    return chunks

@uploads_bp.route("/<int:workspace_id>", methods=["POST"])
@login_required
def upload_pdf(workspace_id):
    # 1) authz
    workspace = Workspace.query.get(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    if workspace.owner_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    # 2) file in request
    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "empty filename"}), 400

    # 3) save
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    # 4) extract text
    doc = fitz.open(path)
    text = "".join([page.get_text() for page in doc])

    # 5) single LLM call → summary, plan, videos
    data = generate_study_package(
        raw_text=text,
        course_title=workspace.title,
        # you can pass deadline if your prompt uses it
        deadline=(workspace.deadline.isoformat() if getattr(workspace, "deadline", None) else None)
    ) or {}

    # normalize structure
    summary = data.get("summary", "")
    study_plan = data.get("study_plan", {})
    videos = data.get("videos", [])

    # 6) persist
    rec = UploadedFile(
        filename=filename,
        path=path,
        workspace_id=workspace_id,
        summary=summary,
        study_plan=json.dumps(study_plan, ensure_ascii=False),
        videos=json.dumps(videos, ensure_ascii=False),
    )
    db.session.add(rec)
    db.session.commit()

    chunks = chunk_text(text)
    for chunk_text_, start, end in chunks:
        embedding = embed_text(chunk_text_)  # returns list[float]

        chunk = DocChunk(
            file_id=rec.id,
            workspace_id=workspace_id,
            chunk_text=chunk_text_,
            start_pos=start,
            end_pos=end,
            token_count=len(chunk_text_.split()),  # rough word count
            embedding=embedding,
        )
        db.session.add(chunk)

    db.session.commit()
    # 7) response
    return jsonify({
        "message": "File uploaded & processed",
        "upload_id": rec.id,
        "summary": summary,
        "study_plan": study_plan,
        "videos": videos,
        "chunks_created": len(chunks)
    }), 201


@uploads_bp.route("/<int:workspace_id>", methods=["GET"])
@login_required
def list_uploads(workspace_id):
    # ensure owner
    workspace = Workspace.query.get(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    if workspace.owner_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    uploads = (UploadedFile.query
             .filter_by(workspace_id=workspace_id)
             .order_by(UploadedFile.created_at.desc())
             .all())

    return jsonify([
        {
            "id": u.id,
            "filename": u.filename,
            "summary": u.summary,
            "study_plan": json.loads(u.study_plan) if u.study_plan else {},
            "videos": json.loads(u.videos) if u.videos else []
        }
        for u in uploads
    ])


@uploads_bp.route("/<int:workspace_id>/<int:upload_id>", methods=["GET"])
@login_required
def get_upload(workspace_id, upload_id):
    workspace = Workspace.query.get(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    if workspace.owner_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    rec = UploadedFile.query.filter_by(id=upload_id, workspace_id=workspace_id).first()
    if not rec:
        return jsonify({"error": "upload not found"}), 404

    return jsonify(rec.to_dict())
