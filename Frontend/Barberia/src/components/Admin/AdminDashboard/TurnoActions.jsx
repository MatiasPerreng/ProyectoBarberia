import API_URL from "../../../services/api";
import './TurnoActions.css'

const TurnoActions = ({ turno }) => {
  const cancelar = async () => {
    const ok = confirm(
      `¿Cancelar el turno de ${turno.cliente_nombre}?`
    );
    if (!ok) return;

    await fetch(`${API_URL}/visitas/${turno.id_visita}`, {
      method: "DELETE",
    });

    window.location.reload();
  };

  return (
    <div className="turno-actions">
      <button
        className="turno-btn-cancel"
        title="Cancelar turno"
        onClick={cancelar}
      >
        ✕
      </button>
    </div>
  );
};

export default TurnoActions;
