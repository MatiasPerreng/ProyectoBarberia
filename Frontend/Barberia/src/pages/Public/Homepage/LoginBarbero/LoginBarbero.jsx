import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthContext } from "../../../../auth/AuthContext";
import { jwtDecode } from "jwt-decode";
import "./LoginBarbero.css";

const API_URL = "http://127.0.0.1:8000";

export default function LoginBarbero() {
  const navigate = useNavigate();
  const { login } = useAuthContext();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("🟡 SUBMIT LOGIN");
    setError("");
    setLoading(true);

    try {
      console.log("🟡 FETCH LOGIN...");
      const response = await fetch(`${API_URL}/auth/login-barbero`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      console.log("🟢 RESPONSE STATUS:", response.status);

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Credenciales incorrectas");
      }

      const data = await response.json();
      console.log("🟢 DATA LOGIN:", data);

      // 🔐 Decodificar JWT (FUENTE DE LA VERDAD)
      const decoded = jwtDecode(data.access_token);
      console.log("🟢 JWT DECODED:", decoded);

      const role = decoded.role;

      if (!role) {
        throw new Error("El token no contiene el rol");
      }

      // 🔐 Guardar sesión
      login({
        token: data.access_token,
        role,
      });

      console.log("🟢 LOGIN() EJECUTADO");
      console.log("🟢 ROL FINAL:", role);
      console.log("🟢 NAVEGANDO...");

      if (role === "admin") {
        console.log("➡️ navigate('/admin')");
        navigate("/admin", { replace: true });
      } else {
        console.log("➡️ navigate('/barbero')");
        navigate("/barbero", { replace: true });
      }

    } catch (err) {
      console.error("🔴 ERROR LOGIN:", err);
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
