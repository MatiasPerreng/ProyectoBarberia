import { useEffect, useState } from "react";
import Footer from "../../Footer/Footer";
import "./AgendaAvailability.css";

import { getDisponibilidad } from "../../../services/agenda";


const AgendaAvailability = ({
  servicio,
  barbero,
  onSelectFechaHora,
  onVolver,
}) => {
  const hoy = new Date();

  const [dias, setDias] = useState([]);
  const [fechaSeleccionada, setFechaSeleccionada] = useState(null);
  const [horarios, setHorarios] = useState([]);

  /* =========================
     GENERAR DÍAS DEL MES
  ========================= */
  useEffect(() => {
    const year = hoy.getFullYear();
    const month = hoy.getMonth();
    const totalDias = new Date(year, month + 1, 0).getDate();

    const diasMes = Array.from({ length: totalDias }, (_, i) => {
      const dia = i + 1;
      const fecha = `${year}-${String(month + 1).padStart(2, "0")}-${String(
        dia
      ).padStart(2, "0")}`;

      return {
        dia,
        fecha,
        disponible: new Date(fecha) >= new Date(hoy.toDateString()),
      };
    });

    setDias(diasMes);
  }, []);

  /* =========================
     FETCH HORARIOS
  ========================= */
  const fetchHorarios = async (fecha) => {
    try {
      const data = await getDisponibilidad({
        fecha,
        id_servicio: servicio.id_servicio,
        id_barbero: barbero?.id_barbero,
      });

      setHorarios(data.turnos || []);
    } catch (err) {
      console.error(err);
      setHorarios([]);
    }
  };

  const handleSelectDia = (fecha) => {
    setFechaSeleccionada(fecha);
    setHorarios([]);
    fetchHorarios(fecha);
  };

  return (
    <>
      <div className="booking-overlay">
        <div className="booking-container">
          {/* SIDEBAR */}
          <aside className="booking-sidebar">
            <div className="logo">
              <img src="/logo.jpg" alt="King Barber" />
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
            <button className="btn-volver" onClick={onVolver}>
              ← Volver
            </button>

            <h3>Selecciona la fecha y hora</h3>

            {/* CALENDARIO */}
            <div className="calendar-grid">
              {dias.map((d) => (
                <button
                  key={d.fecha}
                  className={`calendar-day
                    ${d.disponible ? "available" : "disabled"}
                    ${fechaSeleccionada === d.fecha ? "selected" : ""}
                  `}
                  disabled={!d.disponible}
                  onClick={() => handleSelectDia(d.fecha)}
                >
                  {d.dia}
                </button>
              ))}
            </div>

            {/* HORARIOS */}
            {fechaSeleccionada && (
              <div className="horarios-grid">
                {horarios.length === 0 && (
                  <p className="no-horarios">No hay horarios disponibles</p>
                )}

                {horarios.map((hora) => (
                  <button
                    key={hora}
                    className="hora-card"
                    onClick={() =>
                      onSelectFechaHora(`${fechaSeleccionada} ${hora}`)
                    }
                  >
                    {hora}
                  </button>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      <Footer />
    </>
  );
};

export default AgendaAvailability;
