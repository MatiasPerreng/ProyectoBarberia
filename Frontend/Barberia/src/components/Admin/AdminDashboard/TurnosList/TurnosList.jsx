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
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

const formatearFecha = (fechaHoraStr) => {
  const [fecha, hora] = fechaHoraStr.split(" ");
  const [y, m, d] = fecha.split("-").map(Number);

  const date = new Date(y, m - 1, d);
  const diaSemana = dias[date.getDay()];
  const mes = meses[date.getMonth()];

  return {
    fechaTexto: `${diaSemana} ${d} de ${mes}`,
    hora,
  };
};

const TurnosList = ({ filtro }) => {
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    fetch(`${API_URL}/admin/turnos?filtro=${filtro}`)
      .then((res) => res.json())
      .then(setTurnos)
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
              <p>
                <strong>{t.cliente}</strong> se va a hacer{" "}
                <strong>{t.servicio}</strong> con{" "}
                <strong>{t.barbero}</strong>
              </p>

              <small>
                📅 {fechaTexto} · ⏰ {hora}
              </small>
            </div>

            <TurnoActions turno={t} />
          </div>
        );
      })}
    </div>
  );
};

export default TurnosList;
