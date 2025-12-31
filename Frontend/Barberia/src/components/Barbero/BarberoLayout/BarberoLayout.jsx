import "./BarberoLayout.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";
import { useAuthContext } from "../../../auth/AuthContext";
import Footer from "../../Footer/Footer";

const BarberoLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthContext();

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

        {/* =========================
           CONTENT + FOOTER
        ========================= */}
        <main className="barbero-content">
          {/* CONTENIDO REAL */}
          <div className="barbero-content-inner">
            {children}
          </div>

          {/* FOOTER */}
          <Footer />
        </main>
      </div>
    </>
  );
};

export default BarberoLayout;
