import { useEffect, useState } from "react";
import API_URL from "../../../services/api";

const HistorialAgenda = () => {
  const [turnos, setTurnos] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/visitas/historial`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setTurnos(data);
        } else {
          console.error("Respuesta inválida:", data);
          setTurnos([]);
          setError("No se pudo cargar el historial");
        }
      })
      .catch(err => {
        console.error(err);
        setError("Error de conexión");
      });
  }, []);

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div>
      <h2>Historial de agenda</h2>

      {turnos.length === 0 && (
        <p>No hay turnos en el historial</p>
      )}

      {turnos.map(t => (
        <div key={t.id_visita}>
          {new Date(t.fecha_hora).toLocaleString()} –{" "}
          {t.cliente_nombre} {t.cliente_apellido}
        </div>
      ))}
    </div>
  );
};

export default HistorialAgenda;
