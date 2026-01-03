import { useState } from "react";
import API_URL from "../../services/api";
import "./ChangePasswordModal.css";

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

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (form.nueva !== form.repetir) {
      alert("Las contraseñas no coinciden");
      return;
    }

    const res = await fetch(`${API_URL}/perfil/me/password`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        actual: form.actual,
        nueva: form.nueva,
      }),
    });

    if (!res.ok) {
      alert("Contraseña actual incorrecta");
      return;
    }

    alert("Contraseña actualizada");
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
