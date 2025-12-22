import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "../../Footer/Footer";
import SuccessModal from "../../SuccessModal/SuccessModal";
import "./AgendaForm.css";

const AgendaForm = ({ onSubmit }) => {
  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    email: "",
    telefono: "",
  });

  const [errors, setErrors] = useState({});
  const [showSuccess, setShowSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // ---------------- VALIDACIONES ----------------
  const validarEmail = (email) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const validarTelefono = (telefono) =>
    /^[0-9+\s-]{8,15}$/.test(telefono);

  const validate = () => {
    const newErrors = {};

    if (!form.nombre.trim()) {
      newErrors.nombre = "El nombre es obligatorio";
    }

    if (!form.apellido.trim()) {
      newErrors.apellido = "El apellido es obligatorio";
    }

    if (!validarEmail(form.email)) {
      newErrors.email = "Email inválido";
    }

    if (!validarTelefono(form.telefono)) {
      newErrors.telefono = "Teléfono inválido";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ---------------- HANDLERS ----------------
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);

    try {
      await onSubmit(form);
      setShowSuccess(true);
    } catch (err) {
      console.error("Error al agendar:", err);
      alert("Ocurrió un error al agendar el turno");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="booking-overlay">
        <div className="booking-container">

          {/* SIDEBAR */}
          <aside className="booking-sidebar">
            <div className="logo">
              <img src="logo.jpg" alt="King Barber" />
            </div>

            <ul className="steps">
              <li className="step done"><span>✓</span> Servicio</li>
              <li className="step done"><span>✓</span> Personal</li>
              <li className="step done"><span>✓</span> Fecha y hora</li>
              <li className="step active"><span>4</span> Información</li>
            </ul>

            <div className="sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENIDO */}
          <section className="booking-content">
            <h3>Rellena la información</h3>

            <form className="form-grid" onSubmit={handleSubmit} noValidate>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className={errors.email ? "input-error" : ""}
                />
                {errors.email && <small className="error">{errors.email}</small>}
              </div>

              <div className="form-group">
                <label>Teléfono *</label>
                <input
                  type="text"
                  name="telefono"
                  value={form.telefono}
                  onChange={handleChange}
                  className={errors.telefono ? "input-error" : ""}
                />
                {errors.telefono && <small className="error">{errors.telefono}</small>}
              </div>

              <div className="form-group">
                <label>Nombre *</label>
                <input
                  type="text"
                  name="nombre"
                  value={form.nombre}
                  onChange={handleChange}
                  className={errors.nombre ? "input-error" : ""}
                />
                {errors.nombre && <small className="error">{errors.nombre}</small>}
              </div>

              <div className="form-group">
                <label>Apellido *</label>
                <input
                  type="text"
                  name="apellido"
                  value={form.apellido}
                  onChange={handleChange}
                  className={errors.apellido ? "input-error" : ""}
                />
                {errors.apellido && <small className="error">{errors.apellido}</small>}
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  className="btn-confirmar"
                  disabled={loading}
                >
                  {loading ? "Agendando..." : "Confirmar turno"}
                </button>
              </div>

            </form>
          </section>

        </div>
      </div>

      <SuccessModal
        show={showSuccess}
        onClose={() => {
          setShowSuccess(false);
          navigate("/");
        }}
      />

      <Footer />
    </>
  );
};

export default AgendaForm;
