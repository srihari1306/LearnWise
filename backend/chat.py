# chat.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Workspace, DocChunk
from services.llm_service import embed_text, cosine_similarity, answer_question_with_context

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/<int:workspace_id>/chat", methods=["POST"])
@login_required
def chat(workspace_id):
    workspace = Workspace.query.get(workspace_id)
    if not workspace:
        return jsonify({"error": "workspace not found"}), 404
    if workspace.owner_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403
    
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "no question"}), 400

    # Step 1: Embed the question
    q_embedding = embed_text(question)

    # Step 2: Retrieve chunks from DB
    chunks = DocChunk.query.filter_by(workspace_id=workspace.id).all()
    if not chunks:
        return jsonify({"error": "no chunks available"}), 400

    # Step 3: Rank by cosine similarity
    scored = []
    for c in chunks:
        if not c.embedding:
            continue
        score = cosine_similarity(q_embedding, c.embedding)
        scored.append((score, c))
    scored.sort(reverse=True, key=lambda x: x[0])

    # Step 4: Select top-k chunks (e.g., 3)
    top_chunks = scored[:3]
    context = "\n\n".join([c.chunk_text for _, c in top_chunks])
    sources = [{"id": c.id, "text": c.chunk_text[:100]} for _, c in top_chunks]

    # Step 5: Ask Gemini with context
    answer = answer_question_with_context(question, context)

    return jsonify({
        "answer": answer,
        "sources": sources
    })
