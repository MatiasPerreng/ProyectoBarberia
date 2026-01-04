import { useEffect, useState } from "react";
import API_URL from "../../../services/api";
import "./HistorialAgenda.css";

const hoy = new Date().toISOString().split("T")[0];

const HistorialAgenda = () => {
  const [turnos, setTurnos] = useState([]);
  const [error, setError] = useState(null);

  const [fecha, setFecha] = useState(hoy);
  const [modoTodos, setModoTodos] = useState(true);

  useEffect(() => {
    setError(null);

    let url = `${API_URL}/visitas/historial`;
    if (!modoTodos) {
      url += `?fecha=${fecha}`;
    }

    fetch(url, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setTurnos(data);
        } else {
          setTurnos([]);
          setError("No se pudo cargar el historial");
        }
      })
      .catch(() => {
        setError("Error de conexión");
      });
  }, [fecha, modoTodos]);

  if (error) {
    return <p className="kb-error">{error}</p>;
  }

  return (
    <div className="kb-historial">
      <h2 className="kb-title">Historial de agenda</h2>

      {/* 📅 FILTRO */}
      <div className="kb-filtro-fecha">
        <input
          type="date"
          className="kb-date-filter"
          value={fecha}
          onChange={(e) => {
            setFecha(e.target.value);
            setModoTodos(false);
          }}
        />

        {!modoTodos && (
          <button
            type="button"
            className="kb-btn-todos"
            onClick={() => {
              setModoTodos(true);
              setFecha(hoy); // 🔥 nunca vacío
            }}
          >
            Todos
          </button>
        )}
      </div>

      {turnos.length === 0 && (
        <p className="kb-empty">No hay turnos en el historial</p>
      )}

      <div className="kb-list">
        {turnos.map((t) => {
          const fechaTexto = new Date(t.fecha_hora).toLocaleDateString(
            "es-UY",
            {
              day: "2-digit",
              month: "long",
              year: "numeric",
            }
          );

          return (
            <div key={t.id_visita} className="kb-card">
              <p className="kb-text">
                <span className="kb-date">El día {fechaTexto}</span>,{" "}
                <strong>
                  {t.cliente_nombre} {t.cliente_apellido}
                </strong>{" "}
                se hizo{" "}
                <strong className="kb-service">
                  {t.servicio_nombre}
                </strong>{" "}
                con{" "}
                <strong className="kb-barbero">
                  {t.barbero_nombre}
                </strong>.
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HistorialAgenda;
