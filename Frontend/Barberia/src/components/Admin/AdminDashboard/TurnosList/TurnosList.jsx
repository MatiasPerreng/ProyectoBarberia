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

  useEffect(() => {
    if (!filtro) return;

    setLoading(true);

    fetch(`${API_URL}/admin/turnos?filtro=${filtro}`)
      .then((res) => res.json())
      .then((data) => setTurnos(data))
      .finally(() => setLoading(false));
  }, [filtro]);

  if (loading) return <p>Cargando turnos…</p>;
  if (!turnos.length) return <p>No hay turnos</p>;

  return (
    <div className="turnos-list">
      {turnos.map((t) => {
        const { fechaTexto, hora } = formatearFecha(t.fecha_hora);

        return (
          <div key={t.id_visita} className="turno-row">
            <div className="turno-info">
              {/* 👤 Cliente */}
              <p className="turno-cliente">
                <strong>{t.cliente}</strong>
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
