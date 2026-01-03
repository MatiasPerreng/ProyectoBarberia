import "./AdminLayout.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";
import { useAuthContext } from "../../../auth/AuthContext";
import Footer from "../../Footer/Footer";

const AdminLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { logout, user } = useAuthContext();

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
            <NavLink to="/admin" end>Dashboard</NavLink>
            <NavLink to="/admin/mi-agenda">Mi agenda</NavLink>
            <NavLink to="/admin/historial">Historial</NavLink>
            <NavLink to="/admin/perfil">Mi perfil</NavLink>
            <NavLink to="/admin/barberos">Barberos</NavLink>
            <NavLink to="/admin/horarios">Horarios</NavLink>
            <NavLink to="/admin/servicios">Servicios</NavLink>
          </nav>

          <div className="admin-user">
            <div className="admin-user-info">
              <span className="admin-user-name">
                {user?.nombre || "Usuario"}
              </span>
              <span className="admin-user-role">
                {user?.role || "—"}
              </span>
            </div>

            <button className="admin-logout" onClick={logout}>
              Cerrar sesión
            </button>
          </div>
        </aside>

        {/* CONTENT + FOOTER */}
        <main className="admin-content">
          <div className="admin-content-inner">
            {children}
          </div>

          <Footer />
        </main>
      </div>
    </>
  );
};

export default AdminLayout;
