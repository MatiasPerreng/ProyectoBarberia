import { useState } from "react";
import "./HorarioForm.css";

const DIAS_SEMANA = [
  { id: 1, label: "Lunes" },
  { id: 2, label: "Martes" },
  { id: 3, label: "Miércoles" },
  { id: 4, label: "Jueves" },
  { id: 5, label: "Viernes" },
  { id: 6, label: "Sábado" },
];

const normalizarFecha = (v) => (v && v !== "" ? v : null);

const toInputDate = (v) => {
  if (!v) return "";
  return v.slice(0, 10); // YYYY-MM-DD
};

const HorarioForm = ({
  idBarbero,
  horariosExistentes = [],
  onSubmit,
  onClose,
}) => {
  const [form, setForm] = useState({
    dia_semana: "",
    hora_desde: "",
    hora_hasta: "",
    fecha_desde: "",
    fecha_hasta: "",
  });

  const [copiarDesde, setCopiarDesde] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const copiarHorario = () => {
    if (!copiarDesde) return;

    const horario = horariosExistentes.find(
      (h) => h.dia_semana === Number(copiarDesde)
    );

    if (!horario) {
      setError("No hay horario para ese día");
      return;
    }

    setForm((prev) => ({
      ...prev,
      hora_desde: horario.hora_desde,
      hora_hasta: horario.hora_hasta,
      fecha_desde: toInputDate(horario.fecha_desde),
      fecha_hasta: toInputDate(horario.fecha_hasta),
    }));

    setError(null);
  };

  const validate = () => {
    if (
      !form.dia_semana ||
      !form.hora_desde ||
      !form.hora_hasta ||
      !form.fecha_desde ||
      !form.fecha_hasta
    ) {
      return "Todos los campos son obligatorios";
    }

    if (form.hora_desde >= form.hora_hasta) {
      return "La hora desde debe ser menor que la hora hasta";
    }

    if (form.fecha_desde > form.fecha_hasta) {
      return "La fecha desde no puede ser mayor que la fecha hasta";
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit({
        id_barbero: idBarbero,
        dia_semana: Number(form.dia_semana),
        hora_desde: form.hora_desde,
        hora_hasta: form.hora_hasta,
        fecha_desde: normalizarFecha(form.fecha_desde),
        fecha_hasta: normalizarFecha(form.fecha_hasta),
      });
    } catch (err) {
      setError(err.message || "No se pudo guardar el horario");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h3>Nuevo horario</h3>

        {error && <p className="error">{error}</p>}

        {horariosExistentes.length > 0 && (
          <div className="copiar-horario">
            <select
              value={copiarDesde}
              onChange={(e) => setCopiarDesde(e.target.value)}
            >
              <option value="">Copiar horario de…</option>
              {DIAS_SEMANA.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.label}
                </option>
              ))}
            </select>

            <button type="button" onClick={copiarHorario}>
              Copiar
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Día
            <select
              name="dia_semana"
              value={form.dia_semana}
              onChange={handleChange}
            >
              <option value="">Seleccionar día</option>
              {DIAS_SEMANA.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Hora desde
            <input
              type="time"
              name="hora_desde"
              value={form.hora_desde}
              onChange={handleChange}
            />
          </label>

          <label>
            Hora hasta
            <input
              type="time"
              name="hora_hasta"
              value={form.hora_hasta}
              onChange={handleChange}
            />
          </label>

          <label>
            Vigente desde
            <input
              type="date"
              name="fecha_desde"
              value={form.fecha_desde}
              onChange={handleChange}
            />
          </label>

          <label>
            Vigente hasta
            <input
              type="date"
              name="fecha_hasta"
              value={form.fecha_hasta}
              onChange={handleChange}
            />
          </label>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancelar
            </button>

            <button type="submit" disabled={loading}>
              {loading ? "Guardando…" : "Guardar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default HorarioForm;
