import "./AdminLayout.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";

const AdminLayout = ({ children }) => {
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
      <header className="admin-mobile-header">
        <button
          className="admin-hamburger"
          onClick={() => setSidebarOpen(true)}
        >
          ☰
        </button>

        <img src="/logo.jpg" alt="King Barber" />
      </header>

      {/* OVERLAY */}
      {sidebarOpen && (
        <div
          className="admin-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="admin-layout">
        <aside className={`admin-sidebar ${sidebarOpen ? "open" : ""}`}>
          <div className="admin-logo">
            <img src="/logo.jpg" alt="King Barber" />
          </div>

          <nav className="admin-nav">
            <NavLink to="/admin" end onClick={() => setSidebarOpen(false)}>
              Dashboard
            </NavLink>
            <NavLink to="/admin/barberos" onClick={() => setSidebarOpen(false)}>
              Barberos
            </NavLink>
            <NavLink to="/admin/horarios" onClick={() => setSidebarOpen(false)}>
              Horarios
            </NavLink>
            <NavLink to="/admin/servicios" onClick={() => setSidebarOpen(false)}>
              Servicios
            </NavLink>
          </nav>

          <div className="admin-user">
            <div className="admin-user-info">
              <span className="admin-user-name">{usuario.nombre}</span>
              <span className="admin-user-role">Administrador</span>
            </div>

            <button className="admin-logout" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
        </aside>

        <main className="admin-content">{children}</main>
      </div>
    </>
  );
};

export default AdminLayout;
