import { useEffect, useState } from "react";
import { getAgendaBarbero } from "../../services/agenda";

export default function BarberAgenda() {
  const [agenda, setAgenda] = useState([]);
  const [loading, setLoading] = useState(true);

  // HARDCODEADO por ahora
  const ID_BARBERO = 1;

  useEffect(() => {
    getAgendaBarbero(ID_BARBERO)
      .then(setAgenda)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Cargando agenda...</p>;

  return (
    <div>
      <h2>Mi agenda</h2>

      {agenda.length === 0 && <p>No hay turnos</p>}

      {agenda.map((turno, idx) => (
        <div key={idx} style={{ borderBottom: "1px solid #ccc" }}>
          <strong>{turno.hora}</strong> — {turno.servicio.nombre}
          <br />
          Cliente: {turno.cliente.nombre}
        </div>
      ))}
    </div>
  );
}
