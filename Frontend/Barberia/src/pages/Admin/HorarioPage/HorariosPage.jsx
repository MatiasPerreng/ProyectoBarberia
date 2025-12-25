import { useEffect, useState } from "react";
import AdminLayout from "../../../components/Admin/AdminLayout/AdminLayout";
import HorarioForm from "../../../components/Admin/HorarioForm";
import HorarioList from "../../../components/Admin/HorarioList";

import { getBarberos } from "../../../services/barberos";
import {
  getHorariosBarbero,
  crearHorario,
  eliminarHorario,
} from "../../../services/horarios";

/**
 * Mueve una fecha ISO (YYYY-MM-DD) al PRÓXIMO día de la semana indicado
 * NUNCA va hacia atrás en el calendario
 */
const moverFechaAlProximoDia = (fechaISO, diaDestino) => {
  const fecha = new Date(fechaISO);
  const diaActual = fecha.getDay() === 0 ? 7 : fecha.getDay(); // 1-7

  let diff = diaDestino - diaActual;
  if (diff <= 0) diff += 7; // 🔑 siempre hacia adelante

  fecha.setDate(fecha.getDate() + diff);
  return fecha.toISOString().slice(0, 10);
};

const HorariosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);

  const [horarios, setHorarios] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ----------------------------
  // Cargar barberos
  // ----------------------------
  useEffect(() => {
    getBarberos()
      .then(setBarberos)
      .catch(() => setError("Error al cargar barberos"));
  }, []);

  // ----------------------------
  // Cargar horarios del barbero
  // ----------------------------
  useEffect(() => {
    if (!barberoSeleccionado) {
      setHorarios([]);
      return;
    }

    setLoading(true);
    setError(null);

    getHorariosBarbero(barberoSeleccionado)
      .then(setHorarios)
      .catch(() => setError("Error al cargar horarios"))
      .finally(() => setLoading(false));
  }, [barberoSeleccionado]);

  // ----------------------------
  // Crear horario (desde form)
  // ----------------------------
  const handleCreate = async (data) => {
    try {
      await crearHorario(data);
      setShowForm(false);

      const updated = await getHorariosBarbero(barberoSeleccionado);
      setHorarios(updated);
    } catch (err) {
      setError(err.message || "No se pudo crear el horario");
    }
  };

  // ----------------------------
  // Eliminar horario
  // ----------------------------
  const handleDelete = async (idHorario) => {
    if (!confirm("¿Eliminar este horario?")) return;

    try {
      await eliminarHorario(idHorario);
      const updated = await getHorariosBarbero(barberoSeleccionado);
      setHorarios(updated);
    } catch {
      setError("No se pudo eliminar el horario");
    }
  };

  // ----------------------------
  // COPIAR HORARIO (LÓGICA CORRECTA)
  // ----------------------------
  const handleCopy = async (horario, nuevoDia) => {
    try {
      // 1️⃣ mover fecha_desde al próximo día correcto
      const nuevaFechaDesde = moverFechaAlProximoDia(
        horario.fecha_desde,
        nuevoDia
      );

      // 2️⃣ calcular duración original en días
      const d1 = new Date(horario.fecha_desde);
      const d2 = new Date(horario.fecha_hasta);
      const duracionDias = Math.round(
        (d2 - d1) / (1000 * 60 * 60 * 24)
      );

      // 3️⃣ nueva fecha_hasta = nueva fecha_desde + duración
      const nuevaFechaHasta = new Date(nuevaFechaDesde);
      nuevaFechaHasta.setDate(
        nuevaFechaHasta.getDate() + duracionDias
      );

      await crearHorario({
        id_barbero: horario.id_barbero,
        dia_semana: nuevoDia,
        hora_desde: horario.hora_desde,
        hora_hasta: horario.hora_hasta,
        fecha_desde: nuevaFechaDesde,
        fecha_hasta: nuevaFechaHasta
          .toISOString()
          .slice(0, 10),
      });

      const updated = await getHorariosBarbero(barberoSeleccionado);
      setHorarios(updated);
    } catch (err) {
      setError(err.message || "No se pudo copiar el horario");
    }
  };

  return (
    <AdminLayout>
      <div className="admin-page-header">
        <h2>Horarios</h2>

        <select
          value={barberoSeleccionado ?? ""}
          onChange={(e) =>
            setBarberoSeleccionado(
              e.target.value ? Number(e.target.value) : null
            )
          }
        >
          <option value="">Seleccionar barbero</option>
          {barberos.map((b) => (
            <option key={b.id_barbero} value={b.id_barbero}>
              {b.nombre}
            </option>
          ))}
        </select>

        {barberoSeleccionado && (
          <button onClick={() => setShowForm(true)}>
            + Nuevo horario
          </button>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {loading && <p>Cargando horarios…</p>}

      {!loading && barberoSeleccionado && (
        <HorarioList
          horarios={horarios}
          onDelete={handleDelete}
          onCopy={handleCopy}
        />
      )}

      {showForm && (
        <HorarioForm
          idBarbero={barberoSeleccionado}
          horariosExistentes={horarios}
          onSubmit={handleCreate}
          onClose={() => setShowForm(false)}
        />
      )}
    </AdminLayout>
  );
};

export default HorariosPage;
