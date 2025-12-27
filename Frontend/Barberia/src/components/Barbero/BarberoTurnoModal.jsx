import { useState } from "react";
import CancelarTurnoModal from "./BarberoCancelarTurnoModal";

const BarberoTurnoModal = ({
  turno,
  onClose,
  onAtender,
  onCancelar,
}) => {
  const [cancelar, setCancelar] = useState(false);

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{turno.cliente}</h2>

        <p><strong>Hora:</strong> {turno.hora}</p>
        <p><strong>Servicio:</strong> {turno.servicio}</p>
        <p><strong>Estado:</strong> {turno.estado}</p>

        <div className="acciones">
          {turno.estado === "CONFIRMADO" && (
            <>
              <button onClick={() => onAtender(turno.id)}>
                Marcar atendido
              </button>
              <button
                className="danger"
                onClick={() => setCancelar(true)}
              >
                Cancelar turno
              </button>
            </>
          )}

          <button onClick={onClose}>Cerrar</button>
        </div>
      </div>

      {cancelar && (
        <CancelarTurnoModal
          onConfirm={(motivo) =>
            onCancelar(turno.id, motivo)
          }
          onCancel={() => setCancelar(false)}
        />
      )}
    </div>
  );
};

export default BarberoTurnoModal;
