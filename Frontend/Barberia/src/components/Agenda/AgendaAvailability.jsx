import { useState } from "react";
import Footer from "../Footer/Footer"; // ajustá la ruta si hace falta
import "./AgendaAvailability.css";

const AgendaAvailability = ({ servicio, barbero, onSelectFechaHora }) => {
  const [fecha, setFecha] = useState("");
  const [horarios, setHorarios] = useState([]);

  const fetchDisponibilidad = (fechaSeleccionada) => {
    let url = `http://localhost:8000/visitas/disponibilidad?fecha=${fechaSeleccionada}&id_servicio=${servicio.id_servicio}`;

    if (barbero) {
      url += `&id_barbero=${barbero.id_barbero}`;
    }

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
                <span>✓</span> Servicio
              </li>
              <li className="step done">
                <span>✓</span> Personal
              </li>
              <li className="step active">
                <span>3</span> Fecha y hora
              </li>
              <li className="step">
                <span>4</span> Información
              </li>
            </ul>

            <div className="sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENIDO */}
          <section className="booking-content">
            <h3>Seleccionar fecha y hora</h3>

            {/* CALENDARIO */}
            <div className="calendar-wrapper">
              <input
                type="date"
                value={fecha}
                onChange={handleFechaChange}
                className="calendar-input"
              />
            </div>

            {/* HORARIOS */}
            <div className="horarios-wrapper">
              {horarios.length === 0 && fecha && (
                <p className="no-horarios">
                  No hay horarios disponibles para este día
                </p>
              )}

              {horarios.map(hora => (
                <button
                  key={hora}
                  type="button"
                  className="hora-chip"
                  onClick={() => handleHoraClick(hora)}
                >
                  {hora}
                </button>
              ))}
            </div>
          </section>

        </div>
      </div>

      {/* FOOTER GLOBAL */}
      <Footer />
    </>
  );
};

export default AgendaAvailability;
