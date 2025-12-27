import BarberoAgendaItem from "./BarberoAgendaItem";

const BarberoAgendaList = ({ turnos, onSelectTurno }) => {
  if (!turnos.length) {
    return <p>No tenés turnos hoy</p>;
  }

  return (
    <div className="barbero-agenda-list">
      {turnos.map((turno) => (
        <BarberoAgendaItem
          key={turno.id}
          turno={turno}
          onClick={() => onSelectTurno(turno)}
        />
      ))}
    </div>
  );
};

export default BarberoAgendaList;
