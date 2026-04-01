import { useState, useEffect } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuthContext } from "../../../../auth/AuthContext";
import { jwtDecode } from "jwt-decode";
import Footer from "../../../../components/Footer/Footer";
import "./LoginBarbero.css";

const API_URL = import.meta.env.VITE_API_URL;

export default function LoginBarbero() {
  const navigate = useNavigate();
  const { login, user } = useAuthContext();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  /* Sin scroll en documento (móvil): el footer no queda “debajo” del viewport */
  useEffect(() => {
    const html = document.documentElement;
    const body = document.body;
    const prevHtmlOverflow = html.style.overflow;
    const prevBodyOverflow = body.style.overflow;
    const prevBodyHeight = body.style.height;
    html.style.overflow = "hidden";
    body.style.overflow = "hidden";
    body.style.height = "100%";
    return () => {
      html.style.overflow = prevHtmlOverflow;
      body.style.overflow = prevBodyOverflow;
      body.style.height = prevBodyHeight;
    };
  }, []);

  if (user?.token && user?.role) {
    if (user.role === "admin") {
      return <Navigate to="/admin" replace />;
    }
    return <Navigate to="/barbero" replace />;
  }

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
      const decoded = jwtDecode(data.access_token);
      const role = decoded.role;

      if (!role) {
        throw new Error("El token no contiene el rol");
      }

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
    <div className="kb-login-shell">
      <div className="kb-login-bg" aria-hidden="true" />
      <div className="kb-login-bg-mesh" aria-hidden="true" />

      <div className="kb-login-scroll">
        <main className="kb-login-main">
          <div className="kb-login-panel">
            <header className="kb-login-brand-zone">
              <div className="kb-login-logo-wrap">
                <img
                  src="/logo.jpg"
                  alt="King Barber"
                  className="kb-login-logo"
                  width={84}
                  height={84}
                />
              </div>
              <h1 className="kb-login-brand-title">
                <span className="kb-login-brand-king">KING</span>{" "}
                <span className="kb-login-brand-barber">BARBER</span>
              </h1>
              <p className="kb-login-brand-sub">Acceso para equipo</p>
            </header>

            <form className="kb-login-form" onSubmit={handleSubmit} noValidate>
              <h2 className="kb-login-form-title">Iniciar sesión</h2>
              <p className="kb-login-form-lead">
                Ingresá con tu correo y contraseña asignados.
              </p>

              <div className="kb-login-fields">
                <label className="kb-login-field" htmlFor="kb-login-email">
                  <span className="kb-login-label">Correo</span>
                  <input
                    id="kb-login-email"
                    type="email"
                    name="email"
                    autoComplete="email"
                    inputMode="email"
                    placeholder="correo@ejemplo.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </label>

                <label className="kb-login-field" htmlFor="kb-login-password">
                  <span className="kb-login-label">Contraseña</span>
                  <input
                    id="kb-login-password"
                    type="password"
                    name="password"
                    autoComplete="current-password"
                    placeholder="Tu contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </label>
              </div>

              {error && (
                <div className="kb-login-error" role="alert">
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="kb-login-submit"
                disabled={loading}
              >
                {loading ? "Ingresando…" : "Entrar"}
              </button>
            </form>
          </div>
        </main>
      </div>

      <div className="kb-login-footer-slot">
        <Footer />
      </div>
    </div>
  );
}
