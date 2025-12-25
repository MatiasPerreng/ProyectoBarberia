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

  const [mesActual, setMesActual] = useState(hoy.getMonth());
  const [anioActual, setAnioActual] = useState(hoy.getFullYear());

  const [dias, setDias] = useState([]);
  const [fechaSeleccionada, setFechaSeleccionada] = useState(null);
  const [horarios, setHorarios] = useState([]);

  const meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
  ];

  const diasSemana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

  /* =========================
     GENERAR DÍAS DEL MES
  ========================= */
  useEffect(() => {
    const primerDiaMes = new Date(anioActual, mesActual, 1);
    const offset = (primerDiaMes.getDay() + 6) % 7; // lunes = 0

    const totalDias = new Date(anioActual, mesActual + 1, 0).getDate();

    const diasMes = [];

    // huecos antes del día 1
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
    } catch {
      setHorarios([]);
    }
  };

  const handleSelectDia = (fecha) => {
    setFechaSeleccionada(fecha);
    setHorarios([]);
    fetchHorarios(fecha);
  };

  /* =========================
     CAMBIO DE MES
  ========================= */
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
      <div className="booking-overlay">
        <div className="booking-container">
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

          <section className="booking-content">
            <button className="btn-volver" onClick={onVolver}>
              ← Volver
            </button>

            <h3>Selecciona la fecha y hora</h3>

            {/* HEADER MES */}
            <div className="calendar-header">
              <button className="month-btn" onClick={mesAnterior}>‹</button>
              <span className="month-label">
                {meses[mesActual]} {anioActual}
              </span>
              <button className="month-btn" onClick={mesSiguiente}>›</button>
            </div>

            {/* HEADER DIAS SEMANA */}
            <div className="calendar-weekdays">
              {diasSemana.map((d) => (
                <span key={d}>{d}</span>
              ))}
            </div>

            {/* CALENDARIO */}
            <div className="calendar-grid">
              {dias.map((d, idx) =>
                d.empty ? (
                  <div key={idx} className="calendar-empty" />
                ) : (
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
                )
              )}
            </div>

            {/* HORARIOS */}
            {fechaSeleccionada && (
              <div className="horarios-grid">
                {horarios.length === 0 && (
                  <p className="no-horarios">
                    No hay horarios disponibles
                  </p>
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
