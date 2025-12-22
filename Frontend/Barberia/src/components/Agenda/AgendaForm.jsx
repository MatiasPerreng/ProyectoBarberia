import { useState } from "react";
import Footer from "../Footer/Footer"; // ajustá la ruta si hace falta
import "./AgendaForm.css";

const AgendaForm = ({ onSubmit }) => {
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [email, setEmail] = useState("");
  const [telefono, setTelefono] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      nombre,
      apellido,
      email,
      telefono,
    });
  };

  return (
    <>
      {/* OVERLAY */}
      <div className="booking-overlay">
        <div className="booking-container">

          {/* SIDEBAR */}
          <aside className="booking-sidebar">
            <div className="logo">
              <img src="logo.jpg" alt="King Barber" />
            </div>

            <ul className="steps">
              <li className="step done">
                <span>✓</span> Personal
              </li>
              <li className="step done">
                <span>✓</span> Fecha y hora
              </li>
              <li className="step active">
                <span>3</span> Información
              </li>
            </ul>

            <div className="sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENIDO */}
          <section className="booking-content">
            <h3>Rellena la información</h3>

            <form className="form-grid" onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ejemplo@email.com"
                  required
                />
              </div>

              <div className="form-group">
                <label>Teléfono *</label>
                <input
                  type="text"
                  value={telefono}
                  onChange={(e) => setTelefono(e.target.value)}
                  placeholder="+598 9 123 456"
                  required
                />
              </div>

              <div className="form-group">
                <label>Nombre *</label>
                <input
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Apellido *</label>
                <input
                  type="text"
                  value={apellido}
                  onChange={(e) => setApellido(e.target.value)}
                  required
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-confirmar">
                  Confirmar turno
                </button>
              </div>
            </form>
          </section>

        </div>
      </div>

      {/* FOOTER GLOBAL */}
      <Footer />
    </>
  );
};

export default AgendaForm;
