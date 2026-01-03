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
  const date = new Date(fechaHoraStr);

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
// FILTRO DE TURNOS VIGENTES
// -----------------------------
const turnoSigueVigente = (fechaHoraStr, duracionMin) => {
  const inicio = new Date(fechaHoraStr);

  // Si no hay duración, solo validamos que no sea pasado
  if (!duracionMin || isNaN(duracionMin)) {
    return inicio > new Date();
  }

  const fin = new Date(inicio.getTime() + duracionMin * 60000);
  return fin > new Date();
};

const TurnosList = ({ filtro }) => {
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    fetch(`${API_URL}/admin/turnos?filtro=${filtro}`)
      .then((res) => res.json())
      .then((data) => setTurnos(data))
      .finally(() => setLoading(false));
  }, [filtro]);

  if (loading) return <p>Cargando turnos…</p>;

  const turnosVigentes = turnos.filter((t) => {
    if (t.estado === "CANCELADO" || t.estado === "COMPLETADO") {
      return false;
    }

    return turnoSigueVigente(
      t.fecha_hora,
      t.servicio_duracion
    );
  });

  if (!turnosVigentes.length) {
    return <p>No hay turnos vigentes</p>;
  }

  return (
    <div className="turnos-list">
      {turnosVigentes.map((t) => {
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
