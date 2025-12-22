import "./SuccessModal.css";

export default function SuccessModal({ show, onClose }) {
  if (!show) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h2>Agendado con éxito</h2>
        <p>Tu turno fue registrado correctamente.</p>

        <button onClick={onClose}>
          Volver al inicio
        </button>
      </div>
    </div>
  );
}
