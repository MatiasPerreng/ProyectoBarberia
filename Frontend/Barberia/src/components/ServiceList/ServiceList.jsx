import React, { useEffect, useState } from 'react';

const ServiciosList = ({ onSelectServicio }) => {
  const [servicios, setServicios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/servicios/')
      .then((res) => res.json())
      .then((data) => {
        setServicios(data);
        setLoading(false);
      })
      .catch((err) => console.error(err));
  }, []);

  if (loading) return <p>Cargando servicios...</p>;

  return (
    <div className="d-flex flex-column align-items-center">
      {servicios.map((servicio) => (
        <button
          key={servicio.id_servicio}  // <- actualizar el key
          className="btn btn-outline-primary mb-2"
          onClick={() => onSelectServicio(servicio)}
        >
          {servicio.nombre} ({servicio.duracion_min} min)  {/* <- actualizar duración */}
        </button>
      ))}
    </div>
  );
};

export default ServiciosList;
