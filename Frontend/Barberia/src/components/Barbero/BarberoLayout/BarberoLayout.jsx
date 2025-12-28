import "./BarberoLayout.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";
import { useAuthContext } from "../../../auth/AuthContext";

const BarberoLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthContext(); // ⬅️ usuario real

  return (
    <>
      {/* =========================
         HEADER MOBILE
      ========================= */}
      <header className="barbero-mobile-header">
        <button
          className="barbero-hamburger"
          onClick={() => setSidebarOpen(true)}
        >
          ☰
        </button>

        <img src="/logo.jpg" alt="King Barber" />
      </header>

      {/* =========================
         OVERLAY
      ========================= */}
      {sidebarOpen && (
        <div
          className="barbero-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* =========================
         LAYOUT
      ========================= */}
      <div className="barbero-layout">
        <aside className={`barbero-sidebar ${sidebarOpen ? "open" : ""}`}>
          {/* LOGO */}
          <div className="barbero-logo">
            <img src="/logo.jpg" alt="King Barber" />
          </div>

          {/* NAV */}
          <nav className="barbero-nav">
            <NavLink to="/barbero" end onClick={() => setSidebarOpen(false)}>
              Mi agenda
            </NavLink>

            <NavLink
              to="/barbero/historial"
              onClick={() => setSidebarOpen(false)}
            >
              Historial
            </NavLink>

            <NavLink
              to="/barbero/perfil"
              onClick={() => setSidebarOpen(false)}
            >
              Mi perfil
            </NavLink>
          </nav>

          {/* USER */}
          <div className="barbero-user">
            <div className="barbero-user-info">
              <span className="barbero-user-name">
                {user?.nombre} {user?.apellido}
              </span>
              <span className="barbero-user-role">
                {user?.rol || "Barbero"}
              </span>
            </div>

            <button className="barbero-logout" onClick={logout}>
              Cerrar sesión
            </button>
          </div>
        </aside>

        {/* CONTENT */}
        <main className="barbero-content">
          {children}
        </main>
      </div>
    </>
  );
};

export default BarberoLayout;
