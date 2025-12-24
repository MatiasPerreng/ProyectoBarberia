import { useState } from "react";
import Footer from "../../Footer/Footer";
import SuccessModal from "../../SuccessModal/SuccessModal";
import "./AgendaForm.css";

const AgendaForm = ({ onSubmit, onVolver }) => {
  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    email: "",
    telefono: "",
  });

  const [errors, setErrors] = useState({});
  const [showSuccess, setShowSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

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

    // email es opcional, pero si viene, debe ser válido
    if (form.email.trim() && !validarEmail(form.email)) {
      newErrors.email = "Email inválido";
    }

    // teléfono es opcional, pero si viene, debe ser válido
    if (form.telefono.trim() && !validarTelefono(form.telefono)) {
      newErrors.telefono = "Teléfono inválido";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ---------------- HANDLERS ----------------

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);

    try {
      // 🔥 FIX DEFINITIVO DEL 422
      await onSubmit({
        ...form,
        email: form.email.trim() || null,
        telefono: form.telefono.trim() || null,
      });

      setShowSuccess(true);
    } catch (err) {
      console.error("Error al agendar:", err);
      alert("Ocurrió un error al agendar el turno");
    } finally {
      setLoading(false);
    }
  };

  // ---------------- RENDER ----------------

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
              <li className="step done">
                <span className="step-number">✓</span>
                <p className="step-text">Servicio</p>
              </li>
              <li className="step done">
                <span className="step-number">✓</span>
                <p className="step-text">Personal</p>
              </li>
              <li className="step done">
                <span className="step-number">✓</span>
                <p className="step-text">Fecha y hora</p>
              </li>
              <li className="step active">
                <span className="step-number">4</span>
                <p className="step-text">Información</p>
              </li>
            </ul>

            <div className="sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENIDO */}
          <section className="booking-content">
            {/* BOTÓN VOLVER */}
            <button className="btn-volver" onClick={onVolver}>
              ← Volver
            </button>

            <h3>Rellená la información</h3>

            <form className="form-grid" onSubmit={handleSubmit} noValidate>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className={errors.email ? "input-error" : ""}
                />
                {errors.email && (
                  <small className="error">{errors.email}</small>
                )}
              </div>

              <div className="form-group">
                <label>Teléfono</label>
                <input
                  type="text"
                  name="telefono"
                  value={form.telefono}
                  onChange={handleChange}
                  className={errors.telefono ? "input-error" : ""}
                />
                {errors.telefono && (
                  <small className="error">{errors.telefono}</small>
                )}
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
                {errors.nombre && (
                  <small className="error">{errors.nombre}</small>
                )}
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
                {errors.apellido && (
                  <small className="error">{errors.apellido}</small>
                )}
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
          window.location.href = "/";
        }}
      />

      <Footer />
    </>
  );
};

export default AgendaForm;
