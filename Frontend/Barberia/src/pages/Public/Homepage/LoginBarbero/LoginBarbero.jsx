import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./LoginBarbero.css";

const API_URL = "http://127.0.0.1:8000";

export default function LoginBarbero() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login-barbero`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Credenciales incorrectas");
      }

      const data = await response.json();

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("barbero", JSON.stringify(data.barbero));

      navigate("/barbero/agenda");

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="kb-login-container">
      <form className="kb-login-form" onSubmit={handleSubmit}>
        <img src="/logo.jpg" alt="King Barber" />

        <h2>Acceso Barbero</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Ingresando..." : "Ingresar"}
        </button>

        {error && <p className="kb-login-error">{error}</p>}
      </form>
    </div>
  );
}
