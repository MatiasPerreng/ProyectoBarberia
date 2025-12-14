import { useState, useEffect } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Lobby from './Lobby/Lobby';
import ServiciosList from './ServiceList/ServiceList';
import AgendaForm from './AgendaForm/AgendaForm';

function App() {
  const [view, setView] = useState('lobby'); // 'lobby' | 'servicios' | 'form'
  const [servicioSeleccionado, setServicioSeleccionado] = useState(null);

  // Manejo de envío del turno (cliente + visita)
  const handleSubmitTurno = (turno) => {
    // 1️⃣ Crear cliente primero
    fetch('http://localhost:8000/clientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nombre: turno.nombre,
        apellido: turno.apellido,
        email: turno.email,
        telefono: turno.telefono || null
      })
    })
      .then(res => res.json())
      .then(cliente => {
        console.log({
          id_cliente: cliente.id_cliente,
          id_barbero: turno.id_barbero,
          id_servicio: turno.id_servicio,
          fecha_hora: turno.fecha_hora
        });

        // 2️⃣ Crear visita asociada al cliente
        return fetch('http://localhost:8000/visitas/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id_cliente: cliente.id_cliente,
            id_barbero: turno.id_barbero,
            id_servicio: turno.id_servicio,
            fecha_hora: turno.fecha_hora
          })
        });
      })
      .then(res => res.json())
      .then(data => {
        console.log('Turno agendado', data);
        alert('Turno agendado con éxito!');
        setServicioSeleccionado(null);
        setView('lobby');
      })
      .catch(err => console.error(err));
  };

  // Pasar de lobby a lista de servicios
  const handleAgendaClick = () => {
    setView('servicios');
  };

  // Seleccionar servicio y abrir formulario
  const handleServicioSelect = (servicio) => {
    setServicioSeleccionado(null); // limpiar primero
    setTimeout(() => setServicioSeleccionado(servicio), 0); // luego setear servicio
    setView('form');
  };

  return (
    <div className="App">
      {view === 'lobby' && <Lobby onAgendaClick={handleAgendaClick} />}
      {view === 'servicios' && (
        <ServiciosList onSelectServicio={handleServicioSelect} />
      )}
      {view === 'form' && servicioSeleccionado && (
        <AgendaForm
          servicio={servicioSeleccionado}
          onSubmit={handleSubmitTurno}
        />
      )}
    </div>
  );
}

export default App;
