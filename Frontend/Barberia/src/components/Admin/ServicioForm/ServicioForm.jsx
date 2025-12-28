import { useEffect, useRef, useState } from "react";
import "./ServicioForm.css";

const ServicioForm = ({ servicioInicial, onSubmit, onCancel }) => {
  const [form, setForm] = useState({
    nombre: "",
    precio: "",
    duracion_min: "",
    imagen: null, // 🔥 ahora archivo
  });

  const [preview, setPreview] = useState(null);
  const fileRef = useRef(null);

  useEffect(() => {
    if (servicioInicial) {
      setForm({
        nombre: servicioInicial.nombre ?? "",
        precio: servicioInicial.precio ?? "",
        duracion_min: servicioInicial.duracion_min ?? "",
        imagen: null,
      });

      if (servicioInicial.imagen) {
        setPreview(servicioInicial.imagen);
      }
    }
  }, [servicioInicial]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setForm((prev) => ({ ...prev, imagen: file }));
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      nombre: form.nombre.trim(),
      precio: Number(form.precio),
      duracion_min: Number(form.duracion_min),
      imagen: form.imagen, // 🔥 archivo real
    });
  };

  return (
    <div className="servicio-modal">
      <form className="servicio-form" onSubmit={handleSubmit}>
        <h3>
          {servicioInicial ? "Editar servicio" : "Nuevo servicio"}
        </h3>

        <input
          type="text"
          name="nombre"
          placeholder="Nombre"
          value={form.nombre}
          onChange={handleChange}
          required
        />

        <input
          type="number"
          name="precio"
          step="0.01"
          placeholder="Precio"
          value={form.precio}
          onChange={handleChange}
          required
        />

        <input
          type="number"
          name="duracion_min"
          placeholder="Duración (min)"
          value={form.duracion_min}
          onChange={handleChange}
          required
        />

        {/* =========================
            FILE INPUT PRO
        ========================= */}

        <div className="servicio-file">
          <label
            className="servicio-file-btn"
            onClick={() => fileRef.current.click()}
          >
            Seleccionar imagen
          </label>

          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            hidden
          />
        </div>

        {preview && (
          <img
            src={preview}
            alt="Preview"
            className="servicio-preview"
          />
        )}

        <div className="form-actions">
          <button type="button" onClick={onCancel}>
            Cancelar
          </button>
          <button type="submit">
            Guardar
          </button>
        </div>
      </form>
    </div>
  );
};

export default ServicioForm;
