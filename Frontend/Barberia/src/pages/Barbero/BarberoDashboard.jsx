import { useEffect, useState } from "react";
import BarberoDaySummary from "../../components/Barbero/BarberoDaySummary";
import BarberoAgendaList from "../../components/Barbero/BarberoAgendaList";
import BarberoTurnoModal from "../../components/Barbero/BarberoTurnoModal";
import "./BarberoDashboard.css";

const BarberoDashboard = () => {
  const [turnos, setTurnos] = useState([]);
  const [turnoSeleccionado, setTurnoSeleccionado] = useState(null);

  useEffect(() => {
    // MOCK – después va API
    setTurnos([
      {
        id: 1,
        hora: "10:00",
        cliente: "Juan Pérez",
        servicio: "Corte + Barba",
        estado: "CONFIRMADO",
        precio: 700,
      },
      {
        id: 2,
        hora: "11:30",
        cliente: "Martín López",
        servicio: "Corte",
        estado: "CONFIRMADO",
        precio: 500,
      },
    ]);
  }, []);

  const handleAtender = (id) => {
    setTurnos((prev) =>
      prev.map((t) =>
        t.id === id ? { ...t, estado: "ATENDIDO" } : t
      )
    );
    setTurnoSeleccionado(null);
  };

  const handleCancelar = (id, motivo) => {
    setTurnos((prev) =>
      prev.map((t) =>
        t.id === id
          ? { ...t, estado: "CANCELADO_POR_BARBERO", motivo }
          : t
      )
    );
    setTurnoSeleccionado(null);
  };

  return (
    <div className="barbero-dashboard">
      <h1>Mi agenda</h1>

      <BarberoDaySummary turnos={turnos} />

      <BarberoAgendaList
        turnos={turnos}
        onSelectTurno={setTurnoSeleccionado}
      />

      {turnoSeleccionado && (
        <BarberoTurnoModal
          turno={turnoSeleccionado}
          onClose={() => setTurnoSeleccionado(null)}
          onAtender={handleAtender}
          onCancelar={handleCancelar}
        />
      )}
    </div>
  );
};

export default BarberoDashboard;
