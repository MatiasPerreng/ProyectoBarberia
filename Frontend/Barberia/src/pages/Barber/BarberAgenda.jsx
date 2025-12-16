import { useEffect, useState } from "react";
import AgendaTable from "../../components/Barber/AgendaTable";
import { getAgendaBarbero } from "../../services/barberos";
import { actualizarEstadoVisita } from "../../services/visitas";

const BarberAgenda = () => {
  const BARBERO_ID = 1; // fijo por ahora

  const [agenda, setAgenda] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarAgenda();
  }, []);

  const cargarAgenda = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAgendaBarbero(BARBERO_ID);
      setAgenda(data);
    } catch (err) {
      setError("Error al cargar la agenda");
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // ACCIONES SOBRE TURNOS
  // -----------------------------

  const handleCompletar = async (turno) => {
    try {
      await actualizarEstadoVisita(turno.id_visita, "completado");
      cargarAgenda(); // refresca agenda
    } catch (err) {
      alert("No se pudo completar el turno");
    }
  };

  const handleCancelar = async (turno) => {
    const confirmar = window.confirm(
      "¿Seguro que querés cancelar este turno?"
    );
    if (!confirmar) return;

    try {
      await actualizarEstadoVisita(turno.id_visita, "cancelado");
      cargarAgenda(); // refresca agenda
    } catch (err) {
      alert("No se pudo cancelar el turno");
    }
  };

  if (loading) return <p className="mt-4">Cargando agenda...</p>;
  if (error) return <p className="text-danger">{error}</p>;

  return (
    <div className="container mt-4">
      <h2>Agenda del barbero</h2>

      <AgendaTable
        agenda={agenda}
        onCompletar={handleCompletar}
        onCancelar={handleCancelar}
      />
    </div>
  );
};

export default BarberAgenda;
