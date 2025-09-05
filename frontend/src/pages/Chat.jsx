import React, { useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

function Chat() {
  const { workspaceId } = useParams();
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const ask = async (e) => {
    e.preventDefault();
    if (!question) return;
    const res = await api.post(`/chat/${workspaceId}/chat`, { question });
    setChatHistory([...chatHistory, { q: question, a: res.data.answer, sources: res.data.sources }]);
    setQuestion("");
  };

  return (
    <div>
      <h2>Study Chatbot</h2>
      <div>
        {chatHistory.map((c, i) => (
          <div key={i}>
            <p><b>You:</b> {c.q}</p>
            <p><b>Bot:</b> {c.a}</p>
            <small>Sources: {c.sources.map(s => `${s.filename} (p${s.page})`).join(", ")}</small>
            <hr />
          </div>
        ))}
      </div>
      <form onSubmit={ask}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask your syllabus..."
        />
        <button type="submit">Ask</button>
      </form>
    </div>
  );
}

export default Chat;
