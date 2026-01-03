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
  // ⚠️ backend manda "YYYY-MM-DD HH:mm"
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
// FILTRO DE TURNOS VIGENTES
// -----------------------------
const turnoSigueVigente = (fechaHoraStr, duracionMin) => {
  const inicio = new Date(fechaHoraStr.replace(" ", "T"));

  // Si no hay duración, solo validamos que no sea pasado
  if (!duracionMin || isNaN(duracionMin)) {
    return inicio > new Date();
  }

  const fin = new Date(inicio.getTime() + duracionMin * 60000);
  return fin > new Date();
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

  const turnosFiltrados = turnos.filter((t) => {
    // 🟥 CANCELADOS → mostrar tal cual (NO aplicar lógica de vigencia)
    if (filtro === "cancelados") {
      return t.estado?.toLowerCase() === "cancelado";
    }

    // 🟦 HOY / PENDIENTES
    if (
      t.estado === "CANCELADO" ||
      t.estado === "COMPLETADO" ||
      t.estado === "cancelado"
    ) {
      return false;
    }

    return turnoSigueVigente(
      t.fecha_hora,
      t.servicio_duracion
    );
  });

  if (!turnosFiltrados.length) {
    return <p>No hay turnos</p>;
  }

  return (
    <div className="turnos-list">
      {turnosFiltrados.map((t) => {
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

            {/* ❌ En cancelados no hay acciones */}
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
