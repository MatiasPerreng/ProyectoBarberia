import { useState } from "react";
import API_URL from "../../../services/api";
import "./TurnoActions.css";

const TurnoActions = ({ turno, onCancelSuccess }) => {
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const cancelarTurno = async () => {
    try {
      setLoading(true);
      await fetch(`${API_URL}/visitas/${turno.id_visita}/cancelar`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      setShowModal(false);

      // refresco prolijo
      if (onCancelSuccess) {
        onCancelSuccess();
      } else {
        window.location.reload();
      }
    } catch (err) {
      console.error("Error cancelando turno:", err);
      alert("No se pudo cancelar el turno");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* BOTÓN */}
      <div className="turno-actions">
        <button
          className="turno-btn-cancel"
          title="Cancelar turno"
          onClick={() => setShowModal(true)}
        >
          ✕
        </button>
      </div>

      {/* MODAL */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h3>Cancelar turno</h3>

            <p>
              ¿Cancelar el turno de{" "}
              <strong>{turno.cliente_nombre}</strong>?
            </p>

            <p className="modal-sub">
              {new Date(turno.fecha_hora).toLocaleDateString("es-UY")} ·{" "}
              {new Date(turno.fecha_hora).toLocaleTimeString("es-UY", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>

            <div className="modal-actions">
              <button
                className="btn-secondary"
                disabled={loading}
                onClick={() => setShowModal(false)}
              >
                No, volver
              </button>

              <button
                className="btn-danger"
                disabled={loading}
                onClick={cancelarTurno}
              >
                {loading ? "Cancelando..." : "Sí, cancelar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TurnoActions;
