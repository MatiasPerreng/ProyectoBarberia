import { useState } from 'react';

const AgendaAvailability = ({ servicio, barbero, onSelectFechaHora }) => {
  const [fecha, setFecha] = useState('');
  const [horarios, setHorarios] = useState([]);

  const fetchDisponibilidad = (fechaSeleccionada) => {
    let url = `http://localhost:8000/visitas/disponibilidad?fecha=${fechaSeleccionada}&id_servicio=${servicio.id_servicio}`;

    if (barbero) {
      url += `&id_barbero=${barbero.id_barbero}`;
    }

    fetch(url)
      .then(res => res.json())
      .then(data => setHorarios(data.turnos))
      .catch(err => console.error(err));
  };

  const handleFechaChange = (e) => {
    const value = e.target.value;
    setFecha(value);
    fetchDisponibilidad(value);
  };

  const handleHoraClick = (hora) => {
    const fechaHora = `${fecha} ${hora}`;
    onSelectFechaHora(fechaHora);
  };

  return (
    <div className="container mt-4">
      <h3>Elegí día y hora</h3>

      <input
        type="date"
        className="form-control mb-3"
        value={fecha}
        onChange={handleFechaChange}
      />

      <div className="d-flex gap-2 flex-wrap">
        {horarios.map(hora => (
          <button
            key={hora}
            className="btn btn-danger"
            onClick={() => handleHoraClick(hora)}
          >
            {hora}
          </button>

          
        ))}
      </div>
    </div>
  );
};

export default AgendaAvailability;
