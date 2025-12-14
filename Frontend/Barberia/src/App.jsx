import { useState } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import Lobby from './Lobby/Lobby';
import ServiciosList from './ServiceList/ServiceList';
import BarberosList from './BarberoList/BarberoList';
import AgendaAvailability from './AgendaAvailability/AgendaAvailability.JSX';
import AgendaForm from './AgendaForm/AgendaForm';

function App() {
  const [view, setView] = useState('lobby');

  const [servicioSeleccionado, setServicioSeleccionado] = useState(null);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);
  const [fechaHoraSeleccionada, setFechaHoraSeleccionada] = useState(null);

  //------------------------------------------------------------------------------------
  // ENVÍO FINAL DEL TURNO
  //------------------------------------------------------------------------------------
  const handleSubmitTurno = (datosCliente) => {
    fetch('http://localhost:8000/clientes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nombre: datosCliente.nombre,
        email: datosCliente.email,
        telefono: datosCliente.telefono || null
      })
    })
      .then(res => res.json())
      .then(cliente => {
        return fetch('http://localhost:8000/visitas/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id_cliente: cliente.id_cliente,
            id_barbero: barberoSeleccionado?.id_barbero ?? null,
            id_servicio: servicioSeleccionado.id_servicio,
            fecha_hora: fechaHoraSeleccionada
          })
        });
      })
      .then(res => res.json())
      .then(() => {
        alert('Turno agendado con éxito!');
        resetFlow();
      })
      .catch(err => console.error(err));
  };

  //------------------------------------------------------------------------------------
  // FLUJO DE NAVEGACIÓN
  //------------------------------------------------------------------------------------

  const handleAgendaClick = () => {
    setView('servicios');
  };

  const handleServicioSelect = (servicio) => {
    setServicioSeleccionado(servicio);
    setView('barberos');
  };

  const handleBarberoSelect = (barbero) => {
    setBarberoSeleccionado(barbero);
    setView('disponibilidad');
  };

  const handleFechaHoraSelect = (fechaHora) => {
    console.log('FechaHora recibida en App:', fechaHora);
    setFechaHoraSeleccionada(fechaHora);
    setView('form');
  };

  const resetFlow = () => {
    setServicioSeleccionado(null);
    setBarberoSeleccionado(null);
    setFechaHoraSeleccionada(null);
    setView('lobby');
  };

  //------------------------------------------------------------------------------------
  // RENDER
  //------------------------------------------------------------------------------------
  return (
    <div className="App">
      {view === 'lobby' && <Lobby onAgendaClick={handleAgendaClick} />}

      {view === 'servicios' && (
        <ServiciosList onSelectServicio={handleServicioSelect} />
      )}

      {view === 'barberos' && servicioSeleccionado && (
        <BarberosList onSelectBarbero={handleBarberoSelect} />
      )}

      {view === 'disponibilidad' && servicioSeleccionado && (
        <AgendaAvailability
          servicio={servicioSeleccionado}
          barbero={barberoSeleccionado}
          onSelectFechaHora={handleFechaHoraSelect}
        />
      )}

      {view === 'form' && servicioSeleccionado && fechaHoraSeleccionada && (
        <AgendaForm onSubmit={handleSubmitTurno} />
      )}
    </div>
  );
}

export default App;
