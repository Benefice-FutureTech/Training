import React, { useState } from "react";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState("");

  const API_URL = "http://localhost:8000";

  const register = async () => {
    const resp = await fetch(`${API_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (resp.ok) {
      setMessage("User registered!");
    } else {
      setMessage("Registration failed.");
    }
  };

  const login = async () => {
    const resp = await fetch(`${API_URL}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await resp.json();
    if (resp.ok && data.access_token) {
      setToken(data.access_token);
      setMessage("Logged in!");
    } else {
      setMessage("Login failed.");
    }
  };

  const getUsers = async () => {
    const resp = await fetch(`${API_URL}/users/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await resp.json();
    setUsers(data);
  };

  const callProtected = async () => {
    const resp = await fetch(`${API_URL}/protected`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await resp.json();
    setMessage(data.msg || JSON.stringify(data));
  };

  return (
    <div style={{ maxWidth: 400, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>FastAPI Frontend Test</h2>
      <input
        placeholder="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ width: "100%", marginBottom: 8 }}
      />
      <input
        placeholder="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ width: "100%", marginBottom: 8 }}
      />
      <button onClick={register} style={{ width: "100%", marginBottom: 8 }}>Register</button>
      <button onClick={login} style={{ width: "100%", marginBottom: 8 }}>Login</button>
      <button onClick={getUsers} style={{ width: "100%", marginBottom: 8 }}>List Users</button>
      <button onClick={callProtected} style={{ width: "100%", marginBottom: 8 }}>Call Protected</button>
      <div style={{ margin: "16px 0", color: "#333" }}>{message}</div>
      {users.length > 0 && (
        <ul>
          {users.map(u => (
            <li key={u.id}>{u.username}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
