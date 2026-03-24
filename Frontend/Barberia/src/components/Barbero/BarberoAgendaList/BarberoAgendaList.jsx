import BarberoAgendaItem from "../BarberoAgendaItem/BarberoAgendaItem";
import "./BarberoAgendaList.css";

const normalizarTurno = (t) => {
  const fh = t.fecha_hora || t.fechaHora;
  const [datePart, timePart] = fh ? String(fh).split(" ") : ["", ""];
  const hora = timePart || (fh ? new Date(fh).toLocaleTimeString("es-UY", { hour: "2-digit", minute: "2-digit" }) : "");
  return {
    ...t,
    id_visita: t.id_visita || t.id,
    fechaHora: fh,
    servicio: t.servicio || t.servicio_nombre,
    duracion: t.duracion ?? t.servicio_duracion ?? 0,
    telefono: t.telefono || t.cliente_telefono,
    hora,
  };
};

const BarberoAgendaList = ({ turnos, onSelectTurno }) => {
  if (!turnos.length) {
    return <p>No tenés turnos para hoy</p>;
  }

  return (
    <div className="barbero-agenda-list">
      {turnos.map((turno) => {
        const t = normalizarTurno(turno);
        return (
          <BarberoAgendaItem key={t.id_visita} turno={t} />
        );
      })}
    </div>
  );
};

export default BarberoAgendaList;
