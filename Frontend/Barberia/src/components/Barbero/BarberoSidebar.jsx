import { NavLink } from "react-router-dom";

const BarberoSidebar = () => {
  return (
    <aside className="barbero-sidebar">
      <div className="barbero-sidebar-header">
        <h2>Barbero</h2>
      </div>

      <nav className="barbero-nav">
        <NavLink to="/barbero" end>
          🗓 Mi agenda
        </NavLink>

        <NavLink to="/barbero/agenda">
          📋 Agenda completa
        </NavLink>

        {/* Futuro */}
        {/* <NavLink to="/barbero/historial">
          🕘 Historial
        </NavLink> */}
      </nav>
    </aside>
  );
};

export default BarberoSidebar;
