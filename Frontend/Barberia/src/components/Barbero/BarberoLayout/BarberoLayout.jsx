import "./BarberoLayout.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";

const BarberoLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const usuario = {
    nombre: "Matías Perreng",
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <>
      {/* HEADER MOBILE */}
      <header className="barbero-mobile-header">
        <button
          className="barbero-hamburger"
          onClick={() => setSidebarOpen(true)}
        >
          ☰
        </button>

        <img src="/logo.jpg" alt="King Barber" />
      </header>

      {/* OVERLAY */}
      {sidebarOpen && (
        <div
          className="barbero-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="barbero-layout">
        <aside className={`barbero-sidebar ${sidebarOpen ? "open" : ""}`}>
          <div className="barbero-logo">
            <img src="/logo.jpg" alt="King Barber" />
          </div>

          <nav className="barbero-nav">
            <NavLink to="/barbero" end onClick={() => setSidebarOpen(false)}>
              Mi agenda
            </NavLink>

            <NavLink to="/barbero/historial" onClick={() => setSidebarOpen(false)}>
              Historial
            </NavLink>

            <NavLink to="/barbero/perfil" onClick={() => setSidebarOpen(false)}>
              Mi perfil
            </NavLink>
          </nav>

          <div className="barbero-user">
            <div className="barbero-user-info">
              <span className="barbero-user-name">{usuario.nombre}</span>
              <span className="barbero-user-role">Barbero</span>
            </div>

            <button className="barbero-logout" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
        </aside>

        <main className="barbero-content">
          {children}
        </main>
      </div>
    </>
  );
};

export default BarberoLayout;
