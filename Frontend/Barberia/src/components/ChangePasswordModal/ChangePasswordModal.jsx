import { useState } from "react";
import './ChangePasswordModal.css'


export default function ChangePasswordModal({ show, onClose }) {
  const [form, setForm] = useState({
    actual: "",
    nueva: "",
    repetir: "",
  });

  if (!show) return null;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (form.nueva !== form.repetir) {
      alert("Las contraseñas no coinciden");
      return;
    }

    // 👉 acá después va el fetch al backend
    console.log(form);

    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h3>Cambiar contraseña</h3>

        <form onSubmit={handleSubmit}>
          <input
            type="password"
            name="actual"
            placeholder="Contraseña actual"
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="nueva"
            placeholder="Nueva contraseña"
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="repetir"
            placeholder="Repetir nueva contraseña"
            onChange={handleChange}
            required
          />

          <div className="modal-actions">
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
}
