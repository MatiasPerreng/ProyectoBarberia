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

import "./HorarioPage.css";

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

  useEffect(() => {
    getBarberos()
      .then(setBarberos)
      .catch(() => setError("Error al cargar barberos"));
  }, []);

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

  const handleCreate = async (data) => {
    const fechasNormalizadas = normalizarRangoPorDia({
      fecha_desde: data.fecha_desde,
      fecha_hasta: data.fecha_hasta,
      dia_semana: data.dia_semana,
    });

    // 🔥 SI FALLA, EL ERROR SUBE AL MODAL
    await crearHorario({
      ...data,
      dia_semana: Number(data.dia_semana),
      ...fechasNormalizadas,
    });

    const updated = await getHorariosBarbero(barberoSeleccionado);
    setHorarios(updated);
  };

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

  return (
    <>
      <AdminLayout>
        <div className="horarios-header">
          <h2>Horarios</h2>

          <select
            className="horarios-select-barbero"
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
            <button
              className="horarios-btn-primary"
              onClick={() => setShowForm(true)}
            >
              + Nuevo horario
            </button>
          )}
        </div>

        {!barberoSeleccionado && !loading && (
          <div className="horarios-empty">
            <p className="horarios-empty-title">
              Seleccioná un barbero
            </p>
            <p className="horarios-empty-subtitle">
              Elegí un barbero para ver, crear o modificar sus horarios
            </p>
          </div>
        )}

        {error && <p className="horarios-error">{error}</p>}
        {loading && <p>Cargando horarios…</p>}

        {!loading && barberoSeleccionado && (
          <HorarioList
            horarios={horarios}
            onDelete={handleDelete}
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
