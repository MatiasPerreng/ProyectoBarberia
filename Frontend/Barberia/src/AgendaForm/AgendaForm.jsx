import React, { useState, useEffect } from 'react';

const AgendaForm = ({ servicio, onSubmit }) => {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [email, setEmail] = useState('');
  const [fecha, setFecha] = useState('');
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState('');

  // Traer los barberos al montar el componente
  useEffect(() => {
    fetch('http://localhost:8000/barberos/')
      .then(res => res.json())
      .then(data => setBarberos(data))
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();

    const turno = {
      nombre,
      email,
      fecha_hora: fecha,                 // ✅ nombre correcto
      id_servicio: servicio.id_servicio, // ✅ nombre correcto
      id_barbero: parseInt(barberoSeleccionado) // ✅ nombre correcto
    };


    onSubmit(turno);
  };

  return (
    <div className="agenda-form-container">
      <h2>Agendar turno: {servicio.nombre}</h2>
      <form onSubmit={handleSubmit} className="d-flex flex-column align-items-center">
        <input
          type="text"
          placeholder="Nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="form-control mb-2"
          required
        />
        <input
          type="text"
          placeholder="Apellido"
          value={apellido}
          onChange={(e) => setApellido(e.target.value)}
          className="form-control mb-2"
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="form-control mb-2"
          required
        />
        <input
          type="datetime-local"
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
          className="form-control mb-2"
          required
        />

        {/* Select de barberos */}
        <select
          className="form-control mb-2"
          value={barberoSeleccionado}
          onChange={(e) => setBarberoSeleccionado(e.target.value)}
          required
        >
          <option value="">Selecciona un barbero</option>
          {barberos.map((b) => (
            <option key={b.id_barbero} value={b.id_barbero}>
              {b.nombre}
            </option>
          ))}
        </select>

        <button type="submit" className="btn btn-success mt-2">
          Agendar
        </button>
      </form>
    </div>
  );
};

export default AgendaForm;
