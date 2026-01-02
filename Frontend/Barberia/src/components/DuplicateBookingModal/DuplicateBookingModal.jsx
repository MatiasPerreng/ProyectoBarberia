

export default function DuplicateBookingModal({ show, onClose }) {
  if (!show) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h2>No se puede agendar</h2>

        <p>
          Ya tenés un turno registrado para este día.
          <br />
          Si necesitás cambiarlo, primero cancelá el anterior.
        </p>

        <div className="modal-actions">
          <button
            className="modal-btn-confirm"
            onClick={onClose}
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
