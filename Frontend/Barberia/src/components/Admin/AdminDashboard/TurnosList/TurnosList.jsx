import { useEffect, useState } from "react";
import API_URL from "../../../../services/api";
import TurnoActions from "../TurnoActions";

// -----------------------------
// Utils de formato
// -----------------------------
const dias = [
  "Domingo",
  "Lunes",
  "Martes",
  "Miércoles",
  "Jueves",
  "Viernes",
  "Sábado",
];

const meses = [
  "Enero",
  "Febrero",
  "Marzo",
  "Abril",
  "Mayo",
  "Junio",
  "Julio",
  "Agosto",
  "Septiembre",
  "Octubre",
  "Noviembre",
  "Diciembre",
];

const formatearFecha = (fechaHoraStr) => {
  const date = new Date(fechaHoraStr.replace(" ", "T"));

  const diaSemana = dias[date.getDay()];
  const mes = meses[date.getMonth()];

  return {
    fechaTexto: `${diaSemana} ${date.getDate()} de ${mes}`,
    hora: date.toLocaleTimeString("es-UY", {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };
};

// -----------------------------
// COMPONENTE
// -----------------------------
const TurnosList = ({ filtro }) => {
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fecha, setFecha] = useState(""); // 🆕

  // 🔁 Fetch turnos
  useEffect(() => {
    if (!filtro) return;

    setLoading(true);

    let url = `${API_URL}/admin/turnos?filtro=${filtro}`;
    if (fecha) {
      url += `&fecha=${fecha}`;
    }

    fetch(url)
      .then((res) => res.json())
      .then((data) => setTurnos(data))
      .finally(() => setLoading(false));
  }, [filtro, fecha]);

  // 🧼 Limpiar fecha al cambiar filtro
  useEffect(() => {
    setFecha("");
  }, [filtro]);

  if (loading) return <p>Cargando turnos…</p>;

  return (
    <div className="turnos-list">
      {/* 📅 Calendario solo para pendientes y cancelados */}
      {filtro !== "hoy" && (
        <div className="turnos-filtro-fecha">
          <input
            type="date"
            className="turnos-date-filter"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
          />

          <button
            type="button"
            className="turnos-btn-todos"
            onClick={() => setFecha("")}
          >
            Todos
          </button>
        </div>
      )}


      {!turnos.length && <p>No hay turnos</p>}

      {turnos.map((t) => {
        const { fechaTexto, hora } = formatearFecha(t.fecha_hora);

        return (
          <div key={t.id_visita} className="turno-row">
            <div className="turno-info">
              <p className="turno-cliente">
                <strong>
                  {t.cliente_nombre}
                  {t.cliente_apellido && ` ${t.cliente_apellido}`}
                </strong>
              </p>

              {/* ✂️ Servicio + Barbero */}
              <p className="turno-detalle">
                {t.servicio} con <strong>{t.barbero}</strong>
              </p>

              {/* 📅 Fecha */}
              <small className="turno-fecha">
                📅 {fechaTexto} · ⏰ {hora}
              </small>
            </div>

            {/* ❌ En cancelados NO hay acciones */}
            {filtro !== "cancelados" && (
              <TurnoActions turno={t} />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default TurnosList;
