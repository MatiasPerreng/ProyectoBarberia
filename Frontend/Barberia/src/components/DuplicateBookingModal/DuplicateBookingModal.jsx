

export default function DuplicateBookingModal({ show, onClose }) {
  if (!show) return null;

  return (
    <div className="success-modal-overlay">
      <div className="success-modal-card">
        <h2 className="success-modal-title">
          No se puede agendar
        </h2>

        <p className="success-modal-text">
          Ya tenés un turno registrado para este día.
          <br />
          Si necesitás cambiarlo, primero cancelá el anterior.
        </p>

        <div className="success-modal-actions">
          <button
            className="success-modal-btn-confirm"
            onClick={onClose}
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
