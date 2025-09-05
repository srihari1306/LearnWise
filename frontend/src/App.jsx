import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import PrivateRoute from "./components/PrivateRoute";
import Chat from "./pages/Chat";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={<PrivateRoute><Dashboard /></PrivateRoute>}
        />
        <Route
          path="/upload/:workspaceId"
          element={<PrivateRoute><Upload /></PrivateRoute>}
        />
        <Route
          path="/chat/:workspaceId"
          element={<PrivateRoute><Chat /></PrivateRoute>}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
