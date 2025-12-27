import { useEffect, useState } from "react";
import AdminLayout from "../../../components/Admin/AdminLayout/AdminLayout";
import HorarioForm from "../../../components/Admin/HorarioForm/HorarioForm";
import HorarioList from "../../../components/Admin/HorarioList";
import Footer from "../../../components/Footer/Footer";

import { getBarberos } from "../../../services/barberos";
import {
  getHorariosBarbero,
  crearHorario,
  eliminarHorario,
} from "../../../services/horarios";

/* =========================
   UTILS FECHA
========================= */

const parseFechaLocal = (isoDate) => {
  const [y, m, d] = isoDate.split("-").map(Number);
  return new Date(y, m - 1, d);
};

const normalizarRangoPorDia = ({
  fecha_desde,
  fecha_hasta,
  dia_semana,
}) => {
  const desde = parseFechaLocal(fecha_desde);
  const hasta = parseFechaLocal(fecha_hasta);

  const diaActual = desde.getDay() === 0 ? 7 : desde.getDay();
  const diaDestino = Number(dia_semana);

  let diff = diaDestino - diaActual;
  if (diff < 0) diff += 7;

  if (diff === 0) {
    return { fecha_desde, fecha_hasta };
  }

  const nuevaDesde = new Date(desde);
  nuevaDesde.setDate(nuevaDesde.getDate() + diff);

  const nuevaHasta = new Date(hasta);
  nuevaHasta.setDate(nuevaHasta.getDate() + diff);

  return {
    fecha_desde: nuevaDesde.toISOString().slice(0, 10),
    fecha_hasta: nuevaHasta.toISOString().slice(0, 10),
  };
};

/* =========================
   PAGE
========================= */

const HorariosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);

  const [horarios, setHorarios] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /* -------------------------
     CARGAR BARBEROS
  -------------------------- */
  useEffect(() => {
    getBarberos()
      .then(setBarberos)
      .catch(() => setError("Error al cargar barberos"));
  }, []);

  /* -------------------------
     CARGAR HORARIOS
  -------------------------- */
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

  /* -------------------------
     CREAR HORARIO
  -------------------------- */
  const handleCreate = async (data) => {
    try {
      const fechasNormalizadas = normalizarRangoPorDia({
        fecha_desde: data.fecha_desde,
        fecha_hasta: data.fecha_hasta,
        dia_semana: data.dia_semana,
      });

      await crearHorario({
        ...data,
        dia_semana: Number(data.dia_semana),
        ...fechasNormalizadas,
      });

      setShowForm(false);

      const updated = await getHorariosBarbero(barberoSeleccionado);
      setHorarios(updated);
    } catch (err) {
      setError(err.message || "No se pudo crear el horario");
    }
  };

  /* -------------------------
     ELIMINAR HORARIO
  -------------------------- */
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

  /* -------------------------
     COPIAR HORARIO
  -------------------------- */
  const handleCopy = async (horario, nuevoDia) => {
    try {
      const fechasNormalizadas = normalizarRangoPorDia({
        fecha_desde: horario.fecha_desde,
        fecha_hasta: horario.fecha_hasta,
        dia_semana: nuevoDia,
      });

      await crearHorario({
        id_barbero: horario.id_barbero,
        dia_semana: Number(nuevoDia),
        hora_desde: horario.hora_desde,
        hora_hasta: horario.hora_hasta,
        ...fechasNormalizadas,
      });

      const updated = await getHorariosBarbero(barberoSeleccionado);
      setHorarios(updated);
    } catch (err) {
      setError(err.message || "No se pudo copiar el horario");
    }
  };

  return (
    <>
      <AdminLayout>
        <div className="admin-page-header">
          <h2>Horarios</h2>

          <select
            className="admin-select-barbero"
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

      <Footer />
    </>
  );
};

export default HorariosPage;
