import { useState } from "react";

const CancelarTurnoModal = ({ onConfirm, onCancel }) => {
  const [motivo, setMotivo] = useState("");

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>Cancelar turno</h3>

        <textarea
          placeholder="Motivo (opcional)"
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
        />

        <div className="acciones">
          <button
            className="danger"
            onClick={() => onConfirm(motivo)}
          >
            Confirmar cancelación
          </button>
          <button onClick={onCancel}>Volver</button>
        </div>
      </div>
    </div>
  );
};

export default CancelarTurnoModal;
