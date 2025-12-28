import TurnosList from "./TurnosList/TurnosList";
import BarberoAgendaView from "./BarberoAgendaView";
import './DashboardDrawer.css'

const DashboardDrawer = ({ open, type, onClose }) => {
  if (!open) return null;

  return (
    <div className="dashboard-drawer">
      <div className="drawer-panel">   {/* 👈 ESTE FALTABA */}
        <div className="drawer-header">
          <h2>{type}</h2>
          <button onClick={onClose}>✕</button>
        </div>

        <div className="drawer-content">
          {type === "pendientes" && <TurnosList filtro="pendientes" />}
          {type === "hoy" && <TurnosList filtro="hoy" />}
          {type === "barberos" && <BarberoAgendaView />}
        </div>
      </div>
    </div>
  );
};

export default DashboardDrawer;
