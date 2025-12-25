import "./AdminLayout.css";
import { NavLink } from "react-router-dom";

const AdminLayout = ({ children }) => {
  return (
    <div className="admin-layout">
      {/* SIDEBAR */}
      <aside className="admin-sidebar">
        <div className="admin-logo">
          <img src="/logo.jpg" alt="King Barber" />
        </div>

        <nav className="admin-nav">
          <NavLink to="/admin" end>
            Dashboard
          </NavLink>
          <NavLink to="/admin/barberos">
            Barberos
          </NavLink>
          <NavLink to="/admin/horarios">
            Horarios
          </NavLink>
        </nav>
      </aside>

      {/* CONTENT */}
      <main className="admin-content">
        {children}
      </main>
    </div>
  );
};

export default AdminLayout;
