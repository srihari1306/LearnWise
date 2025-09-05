import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function Dashboard() {
  const [workspaces, setWorkspaces] = useState([]);
  const [title, setTitle] = useState("");
  const [deadline, setDeadline] = useState("");
  const [uploads, setUploads] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const fetchWorkspaces = async () => {
    const res = await api.get("/workspaces/");
    setWorkspaces(res.data);
  };

  const fetchUploads = async (workspaceId) => {
    const res = await api.get(`/uploads/${workspaceId}`);
    setUploads((prev) => ({ ...prev, [workspaceId]: res.data }));
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post("/workspaces/", { title, deadline });
    setTitle("");
    setDeadline("");
    fetchWorkspaces();
  };

  const handleLogout = async () => {
    await api.post("/auth/logout");
    navigate("/login");
  };

  return (
    <div>
      <h2>Dashboard</h2>
      <form onSubmit={handleCreate}>
        <input
          placeholder="Workspace title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          type="date"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
        />
        <button type="submit">Create</button>
      </form>

      <h3>My Workspaces</h3>
      <ul>
        {workspaces.map((w) => (
          <li key={w.id}>
            <strong>{w.title}</strong> (Deadline: {w.deadline || "none"}){" "}
            <button onClick={() => navigate(`/upload/${w.id}`)}>Upload</button>
            <button onClick={() => fetchUploads(w.id)}>View Uploads</button>
            <button onClick={() => navigate(`/chat/${w.id}`)}>Chat</button>

            {uploads[w.id] && (
  <ul style={{ marginTop: "10px" }}>
    {uploads[w.id].map((u) => (
      <li key={u.id} style={{ marginBottom: "20px", padding: "10px", border: "1px solid #ccc", borderRadius: "8px" }}>
        <h4>📄 {u.filename}</h4>

        <p><strong>Summary:</strong> {u.summary}</p>

        <div>
          <strong>Study Plan:</strong>
          <ul>
            {Object.entries(u.study_plan || {}).map(([key, value]) => (
              <li key={key}>
                <b>{key}:</b> {value}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <strong>Recommended Videos:</strong>
          <ul>
            {(u.videos || []).map((vid, i) => (
              <li key={i}>
                <a href={vid.url} target="_blank" rel="noopener noreferrer">
                  {vid.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </li>
    ))}
  </ul>
)}

          </li>
        ))}
      </ul>

      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Dashboard;
