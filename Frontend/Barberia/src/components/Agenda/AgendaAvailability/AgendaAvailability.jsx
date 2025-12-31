import { useEffect, useState } from "react";
import Footer from "../../Footer/Footer";
import "./AgendaAvailability.css";

import { getDisponibilidad } from "../../../services/agenda";

/* ======================================================
   VALIDACIÓN HORA (LOCAL TIME)
====================================================== */
const esHoraValida = (fecha, hora) => {
  const ahora = new Date();

  const [y, m, d] = fecha.split("-").map(Number);
  const [h, min] = hora.split(":").map(Number);

  const fechaHora = new Date(y, m - 1, d, h, min, 0, 0);

  return fechaHora > ahora;
};

const AgendaAvailability = ({
  servicio,
  barbero,
  onSelectFechaHora,
  onVolver,
}) => {
  const hoy = new Date();
  const hoyISO = hoy.toISOString().split("T")[0];

  const [mesActual, setMesActual] = useState(hoy.getMonth());
  const [anioActual, setAnioActual] = useState(hoy.getFullYear());

  const [dias, setDias] = useState([]);
  const [fechaSeleccionada, setFechaSeleccionada] = useState(null);
  const [horarios, setHorarios] = useState([]);

  const meses = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre",
  ];

  const diasSemana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

  useEffect(() => {
    const primerDiaMes = new Date(anioActual, mesActual, 1);
    const offset = (primerDiaMes.getDay() + 6) % 7;

    const totalDias = new Date(anioActual, mesActual + 1, 0).getDate();
    const diasMes = [];

    for (let i = 0; i < offset; i++) {
      diasMes.push({ empty: true });
    }

    for (let dia = 1; dia <= totalDias; dia++) {
      const fechaObj = new Date(anioActual, mesActual, dia);
      const fecha = fechaObj.toISOString().split("T")[0];

      diasMes.push({
        dia,
        fecha,
        disponible: fechaObj >= new Date(hoy.toDateString()),
      });
    }

    setDias(diasMes);
    setFechaSeleccionada(null);
    setHorarios([]);
  }, [mesActual, anioActual]);

  const fetchHorarios = async (fecha) => {
    try {
      const data = await getDisponibilidad({
        fecha,
        id_servicio: servicio.id_servicio,
        id_barbero: barbero?.id_barbero,
      });
      setHorarios(data.turnos || []);
    } catch {
      setHorarios([]);
    }
  };

  const handleSelectDia = (fecha) => {
    setFechaSeleccionada(fecha);
    setHorarios([]);
    fetchHorarios(fecha);
  };

  const mesAnterior = () => {
    if (mesActual === 0) {
      setMesActual(11);
      setAnioActual((a) => a - 1);
    } else {
      setMesActual((m) => m - 1);
    }
  };

  const mesSiguiente = () => {
    if (mesActual === 11) {
      setMesActual(0);
      setAnioActual((a) => a + 1);
    } else {
      setMesActual((m) => m + 1);
    }
  };

  return (
    <>
      <div className="aa-booking-overlay">
        <div className="aa-booking-container">
          <aside className="aa-booking-sidebar">
            <div className="aa-logo">
              <img src="/logo.jpg" alt="King Barber" />
            </div>

            <ul className="aa-steps">
              <li className="aa-step done">
                <span className="aa-step-number">✓</span>
                <p className="aa-step-text">Servicio</p>
              </li>
              <li className="aa-step done">
                <span className="aa-step-number">✓</span>
                <p className="aa-step-text">Personal</p>
              </li>
              <li className="aa-step active">
                <span className="aa-step-number">3</span>
                <p className="aa-step-text">Fecha y hora</p>
              </li>
              <li className="aa-step">
                <span className="aa-step-number">4</span>
                <p className="aa-step-text">Información</p>
              </li>
            </ul>

            <div className="aa-sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          <section className="aa-booking-content">
            <button className="aa-btn-volver" onClick={onVolver}>
              ← Volver
            </button>

            <h3>Selecciona la fecha y hora</h3>

            <div className="aa-calendar-header">
              <button className="aa-month-btn" onClick={mesAnterior}>‹</button>
              <span className="aa-month-label">
                {meses[mesActual]} {anioActual}
              </span>
              <button className="aa-month-btn" onClick={mesSiguiente}>›</button>
            </div>

            <div className="aa-calendar-weekdays">
              {diasSemana.map((d) => (
                <span key={d}>{d}</span>
              ))}
            </div>

            <div className="aa-calendar-grid">
              {dias.map((d, idx) =>
                d.empty ? (
                  <div key={idx} className="aa-calendar-empty" />
                ) : (
                  <button
                    key={d.fecha}
                    className={`aa-calendar-day
                      ${d.disponible ? "available" : "disabled"}
                      ${fechaSeleccionada === d.fecha ? "selected" : ""}
                    `}
                    disabled={!d.disponible}
                    onClick={() => handleSelectDia(d.fecha)}
                  >
                    {d.dia}
                  </button>
                )
              )}
            </div>

            {fechaSeleccionada && (
              <div className="aa-horarios-grid">
                {horarios
                  .filter((hora) =>
                    fechaSeleccionada === hoyISO
                      ? esHoraValida(fechaSeleccionada, hora)
                      : true
                  )
                  .map((hora) => (
                    <button
                      key={hora}
                      className="aa-hora-card"
                      onClick={() =>
                        onSelectFechaHora(`${fechaSeleccionada} ${hora}`)
                      }
                    >
                      {hora}
                    </button>
                  ))}

                {horarios.length > 0 &&
                  horarios.filter((hora) =>
                    fechaSeleccionada === hoyISO
                      ? esHoraValida(fechaSeleccionada, hora)
                      : true
                  ).length === 0 && (
                    <p className="aa-no-horarios">
                      No hay horarios disponibles
                    </p>
                  )}
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
