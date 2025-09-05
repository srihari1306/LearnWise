import React, { useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

function Upload() {
  const { workspaceId } = useParams();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setResult(null);
      const res = await api.post(`/uploads/${workspaceId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error uploading file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload PDF</h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Upload"}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>📄 Summary</h3>
          <p>{result.summary}</p>

          <h3>📅 Study Plan</h3>
          <ul>
            {Object.entries(result.study_plan || {}).map(([key, value]) => (
              <li key={key}>
                <strong>{key}:</strong> {value}
              </li>
            ))}
          </ul>

          <h3>🎥 Recommended Videos</h3>
          <ul>
            {(result.videos || []).map((vid, i) => (
              <li key={i}>
                <a href={vid.url} target="_blank" rel="noopener noreferrer">
                  {vid.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Upload;
