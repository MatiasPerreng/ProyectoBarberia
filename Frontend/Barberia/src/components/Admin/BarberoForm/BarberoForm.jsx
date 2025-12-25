import { useState } from "react";
import "./BarberoForm.css";
import { subirFotoBarbero } from "../../../services/barberos";

const BarberoForm = ({ onSubmit, onClose }) => {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [foto, setFoto] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFoto(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 1️⃣ crear barbero
      const barbero = await onSubmit({ nombre, email });

      // 2️⃣ subir foto
      if (foto && barbero?.id_barbero) {
        await subirFotoBarbero(barbero.id_barbero, foto);
      }

      onClose();
    } catch (err) {
      alert("Error al crear barbero");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-modal-overlay">
      <div className="admin-modal">
        <h3>Nuevo barbero</h3>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Nombre"
            value={nombre}
            required
            onChange={(e) => setNombre(e.target.value)}
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
          />

          {/* 👇 FEEDBACK VISUAL */}
          {preview && (
            <img
              src={preview}
              alt="Preview"
              style={{
                width: 100,
                height: 100,
                objectFit: "cover",
                borderRadius: 12,
                marginTop: 8,
              }}
            />
          )}

          <div className="modal-actions">
            <button type="submit" disabled={loading}>
              {loading ? "Creando…" : "Crear"}
            </button>
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BarberoForm;
