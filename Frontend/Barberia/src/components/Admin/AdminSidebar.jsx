import { NavLink } from "react-router-dom";

const AdminSidebar = () => {
  return (
    <aside className="admin-sidebar">
      <div className="admin-logo">
        <img src="/logo.jpg" alt="King Barber" />
        <span>ADMIN</span>
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

        <NavLink to="/admin/turnos">
          Turnos
        </NavLink>
      </nav>
    </aside>
  );
};

export default AdminSidebar;
