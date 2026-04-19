import React, { useEffect, useState } from "react";
import "./ServicesList.css";
import API_URL from "../../services/api";
import { formatFastApiDetail, networkFailureMessage } from "../../utils/apiError";

const ServiciosList = ({ onSelectServicio }) => {
  const [servicios, setServicios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(`${API_URL}/servicios/`)
      .then(async (res) => {
        const body = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(formatFastApiDetail(body) || "No se pudieron cargar los servicios");
        }
        return Array.isArray(body) ? body : [];
      })
      .then((data) => {
        if (!cancelled) {
          setServicios(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (!cancelled) {
          setError(err.message || networkFailureMessage(err));
          setServicios([]);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) return <p className="loading">Cargando servicios...</p>;

  if (error) {
    return (
      <div className="servicios-grid" style={{ padding: "2rem", textAlign: "center" }}>
        <p className="loading">{error}</p>
        <button
          type="button"
          className="btn-reservar"
          onClick={() => window.location.reload()}
          style={{ marginTop: "1rem" }}
        >
          <span>REINTENTAR</span>
        </button>
      </div>
    );
  }

  return (
    <div className="servicios-grid">
      {servicios.map((servicio) => (
        <div className="servicio-card" key={servicio.id_servicio}>
          <div className="servicio-img-wrapper">
            <img
              src={`${API_URL}/media/servicios/${servicio.imagen}`}
              alt={servicio.nombre}
              className="servicio-img"
            />
          </div>

          <div className="servicio-body">
            <h3 className="servicio-title">
              {servicio.nombre.toUpperCase()}
            </h3>

            <span className="servicio-duracion">
              {servicio.duracion_min} MIN.
            </span>

            <p className="servicio-desc">
              {servicio.descripcion || "Servicio profesional de barbería"}
            </p>

            <div className="servicio-footer">
              <span className="servicio-precio">
                <small>$</small>{servicio.precio}
              </span>

              <button
                className="btn-reservar"
                onClick={() => onSelectServicio(servicio)}
              >
                {/* El span es necesario para la animación 3D del texto */}
                <span>RESERVAR AHORA</span>
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ServiciosList;