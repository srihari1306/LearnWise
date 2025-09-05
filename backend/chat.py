# chat.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Workspace, UploadedFile
from services.llm_service import answer_question_with_context
import fitz  # PyMuPDF

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/<int:workspace_id>/chat", methods=["POST"])
@login_required
def chat(workspace_id):
    # Check workspace ownership
    workspace = Workspace.query.get(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    if workspace.owner_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True) or {}
    question = data.get("question")
    if not question:
        return jsonify({"error": "no question"}), 400

    # Get files in this workspace (no relationship on Workspace, so we query)
    files = UploadedFile.query.filter_by(workspace_id=workspace_id).all()
    if not files:
        return jsonify({"error": "no documents uploaded in this workspace"}), 400

    # Build chunks from PDFs (lightweight per-page chunks with provenance)
    chunks = []
    for f in files:
        try:
            with fitz.open(f.path) as doc:
                for idx, page in enumerate(doc, start=1):
                    text = page.get_text()
                    if not text:
                        continue
                    chunks.append({
                        "text": text,
                        "source": f.filename,
                        "page": idx
                    })
        except Exception as e:
            # Skip unreadable files but continue with others
            chunks.append({
                "text": "",
                "source": f.filename,
                "page": None,
                "error": f"Failed to read: {e}"
            })

    # If nothing readable, stop early
    valid_chunks = [c for c in chunks if c.get("text")]
    if not valid_chunks:
        return jsonify({"error": "no readable text found in uploaded PDFs"}), 400

    # Ask the LLM with retrieval context; include provenance
    answer, sources = answer_question_with_context(question, valid_chunks)

    return jsonify({
        "answer": answer,
        "sources": sources  # typically list of {filename, page}
    })
