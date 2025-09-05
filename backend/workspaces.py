from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db,Workspace
from datetime import datetime

workspaces_bp = Blueprint("workspaces", __name__)

@workspaces_bp.route("/", methods=["POST"])
@login_required
def create_workspace():
    data = request.json
    title = data.get("title")
    deadline = data.get("deadline")

    ws = Workspace(
        owner_id=current_user.id,
        title=title,
        deadline=datetime.fromisoformat(deadline) if deadline else None
    )
    db.session.add(ws)
    db.session.commit()

    return jsonify({"ok": True, "workspace_id": ws.id})

@workspaces_bp.route("/", methods=["GET"])
@login_required
def list_workspaces():
    workspaces = Workspace.query.filter_by(owner_id=current_user.id).all()
    return jsonify([
        {"id": w.id, "title": w.title, "deadline": w.deadline.isoformat() if w.deadline else None}
        for w in workspaces
    ])
