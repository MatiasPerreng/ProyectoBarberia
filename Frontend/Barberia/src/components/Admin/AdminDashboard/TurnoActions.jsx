import API_URL from "../../../services/api";

const TurnoActions = ({ turno }) => {
  const cancelar = async () => {
    if (!confirm("¿Cancelar este turno?")) return;

    await fetch(`${API_URL}/visitas/${turno.id_visita}`, {
      method: "DELETE",
    });

    window.location.reload();
  };

  return (
    <div className="turno-actions">
      <button title="Cancelar" onClick={cancelar}>
        ❌
      </button>
    </div>
  );
};

export default TurnoActions;
