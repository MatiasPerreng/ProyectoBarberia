import { useState } from "react";
import "./CreateBarberoAccountModal.css";
import { crearCuentaBarbero } from "../../../services/barberos";

const CreateBarberoAccountModal = ({ barbero, onClose, onSuccess }) => {
  const [form, setForm] = useState({
    email: "",
    password: "",
    rol: "barbero",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await crearCuentaBarbero({
      barbero_id: barbero.id_barbero,
      nombre: barbero.nombre,
      ...form,
    });

    onSuccess();
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h3>Crear acceso</h3>
        <p>
          Barbero: <strong>{barbero.nombre}</strong>
        </p>

        <form onSubmit={handleSubmit}>
          <input
            name="email"
            type="email"
            placeholder="Email"
            required
            onChange={handleChange}
          />

          <input
            name="password"
            type="password"
            placeholder="Contraseña"
            required
            onChange={handleChange}
          />

          <select name="rol" onChange={handleChange}>
            <option value="barbero">Barbero</option>
            <option value="admin">Admin</option>
          </select>

          <div className="modal-actions">
            <button type="submit">Crear</button>
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateBarberoAccountModal;
