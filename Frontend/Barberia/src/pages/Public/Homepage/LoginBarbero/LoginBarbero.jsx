import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthContext } from "../../../../auth/AuthContext";
import { jwtDecode } from "jwt-decode";
import "./LoginBarbero.css";

const API_URL = import.meta.env.VITE_API_URL;

export default function LoginBarbero() {
  const navigate = useNavigate();
  const { login } = useAuthContext();

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
 

      // 🔐 Decodificar JWT (FUENTE DE LA VERDAD)
      const decoded = jwtDecode(data.access_token);

      const role = decoded.role;

      if (!role) {
        throw new Error("El token no contiene el rol");
      }

      // 🔐 Guardar sesión
      login({
        token: data.access_token,
        role,
      });

      if (role === "admin") {
        navigate("/admin", { replace: true });
      } else {
        navigate("/barbero", { replace: true });
      }

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

        <h2>Acceso</h2>

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
