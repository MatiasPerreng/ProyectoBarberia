import { useState } from "react";
import { useNavigate } from "react-router-dom";

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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Error al iniciar sesión");
      }

      const data = await response.json();

      // Guardar sesión
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("barbero", JSON.stringify(data.barbero));

      // 👉 Redirección correcta según tu router
      navigate("/barbero/agenda");

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2>Login Barbero</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={styles.input}
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={styles.input}
        />

        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? "Ingresando..." : "Ingresar"}
        </button>

        {error && <p style={styles.error}>{error}</p>}
      </form>
    </div>
  );
}

//----------------------------------------------------------------------------------------------------------------------
// ESTILOS SIMPLES (después los pasás a CSS / Bootstrap / Tailwind)
//----------------------------------------------------------------------------------------------------------------------

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#111",
  },
  form: {
    width: "100%",
    maxWidth: "350px",
    padding: "2rem",
    borderRadius: "8px",
    background: "#1e1e1e",
    color: "#fff",
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  input: {
    padding: "0.7rem",
    borderRadius: "4px",
    border: "none",
    outline: "none",
  },
  button: {
    padding: "0.7rem",
    borderRadius: "4px",
    border: "none",
    background: "#e11d48",
    color: "#fff",
    fontWeight: "bold",
    cursor: "pointer",
  },
  error: {
    color: "#f87171",
    marginTop: "0.5rem",
    textAlign: "center",
  },
};
