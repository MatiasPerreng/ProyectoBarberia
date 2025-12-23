import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "../../Footer/Footer";
import "./AgendaAvailability.css";

const AgendaAvailability = ({ servicio, barbero, onSelectFechaHora }) => {
  const [fecha, setFecha] = useState("");
  const [horarios, setHorarios] = useState([]);

  const navigate = useNavigate();

  const fetchDisponibilidad = (fechaSeleccionada) => {
    let url = `http://localhost:8000/visitas/disponibilidad?fecha=${fechaSeleccionada}&id_servicio=${servicio.id_servicio}`;
    if (barbero) url += `&id_barbero=${barbero.id_barbero}`;

    fetch(url)
      .then(res => res.json())
      .then(data => setHorarios(data.turnos || []))
      .catch(err => {
        console.error(err);
        setHorarios([]);
      });
  };

  const handleFechaChange = (e) => {
    const value = e.target.value;
    setFecha(value);
    fetchDisponibilidad(value);
  };

  const handleHoraClick = (hora) => {
    const fechaHora = `${fecha} ${hora}`;
    onSelectFechaHora(fechaHora);
  };

  const handleVolver = () => {
      navigate("/agenda");
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
              <li className="step done">
                <span className="step-number">✓</span>
                <p className="step-text">Servicio</p>
              </li>
              <li className="step done">
                <span className="step-number">✓</span>
                <p className="step-text">Personal</p>
              </li>
              <li className="step active">
                <span className="step-number">3</span>
                <p className="step-text">Fecha y hora</p>
              </li>
              <li className="step">
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
            <button className="btn-volver" onClick={handleVolver}>
              ← Volver
            </button>

            <h3>Seleccionar fecha y hora</h3>

            <div className="calendar-wrapper">
              <label className="calendar-label">Elegí el día:</label>
              <input
                type="date"
                value={fecha}
                onChange={handleFechaChange}
                className="calendar-input"
              />
            </div>

            <div className="horarios-grid">
              {horarios.length === 0 && fecha && (
                <p className="no-horarios">No hay horarios disponibles</p>
              )}

              {horarios.map(hora => (
                <button
                  key={hora}
                  type="button"
                  className="hora-card"
                  onClick={() => handleHoraClick(hora)}
                >
                  {hora}
                </button>
              ))}
            </div>
          </section>
        </div>
      </div>

      <Footer />
    </>
  );
};

export default AgendaAvailability;
