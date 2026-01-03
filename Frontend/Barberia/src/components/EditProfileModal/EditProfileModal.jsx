import { useEffect, useState } from "react";
import API_URL from "../../services/api";
import "./EditProfileModal.css";

function EditProfileModal({ show, onClose, user, onSuccess }) {
  const [form, setForm] = useState({
    nombre: "",
    email: "",
  });

  // 🔥 SINCRONIZA CUANDO LLEGA USER
  useEffect(() => {
    if (user) {
      setForm({
        nombre: user.nombre,
        email: user.email,
      });
    }
  }, [user]);

  if (!show) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch(`${API_URL}/perfil/me`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify(form),
    });

    if (!res.ok) {
      alert("Error al actualizar perfil");
      return;
    }

    const data = await res.json();
    onSuccess(data);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h3>Editar perfil</h3>

        <form onSubmit={handleSubmit}>
          <input
            name="nombre"
            value={form.nombre}
            onChange={(e) =>
              setForm({ ...form, nombre: e.target.value })
            }
            required
          />

          <input
            name="email"
            type="email"
            value={form.email}
            onChange={(e) =>
              setForm({ ...form, email: e.target.value })
            }
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

export default EditProfileModal;
