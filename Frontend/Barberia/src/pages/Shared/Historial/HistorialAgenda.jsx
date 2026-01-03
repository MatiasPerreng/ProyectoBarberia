import { useEffect, useState } from "react";
import API_URL from "../../../services/api";
import "./HistorialAgenda.css";

const HistorialAgenda = () => {
  const [turnos, setTurnos] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/visitas/historial`, {
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
  }, []);

  if (error) {
    return <p className="kb-error">{error}</p>;
  }

  return (
    <div className="kb-historial">
      <h2 className="kb-title">Historial de agenda</h2>

      {turnos.length === 0 && (
        <p className="kb-empty">No hay turnos en el historial</p>
      )}

      <div className="kb-list">
        {turnos.map((t) => {
          const fecha = new Date(t.fecha_hora).toLocaleDateString("es-UY", {
            day: "2-digit",
            month: "long",
            year: "numeric",
          });

          return (
            <div key={t.id_visita} className="kb-card">
              <p className="kb-text">
                <span className="kb-date">El día {fecha}</span>,{" "}
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
                </strong>
                .
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HistorialAgenda;
