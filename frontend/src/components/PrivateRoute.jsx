import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api from "../api";

const PrivateRoute = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    api.get("/auth/me")
      .then(() => setAuthed(true))
      .catch(() => setAuthed(false))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  return authed ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
