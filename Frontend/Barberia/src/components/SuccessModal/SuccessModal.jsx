import "./SuccessModal.css";

export default function SuccessModal({ show, onClose }) {
  if (!show) return null;

  return (
    <div className="success-modal-overlay">
      <div className="success-modal-card">
        <h2 className="success-modal-title">
          Agendado con éxito
        </h2>

        <p className="success-modal-text">
          Tu turno fue registrado correctamente.
        </p>

        <div className="success-modal-actions">
          <button
            className="success-modal-btn-confirm"
            onClick={onClose}
          >
            Volver al inicio
          </button>
        </div>
      </div>
    </div>
  );
}
