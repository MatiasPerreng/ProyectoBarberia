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
  const handleSubmitTurno = async (datosCliente) => {
    try {
      // 1️⃣ Crear cliente
      const resCliente = await fetch('http://localhost:8000/clientes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: datosCliente.nombre,
          email: datosCliente.email,
          telefono: datosCliente.telefono || null
        })
      });

      if (!resCliente.ok) {
        throw new Error('Error al crear cliente');
      }

      const cliente = await resCliente.json();
      console.log('Cliente creado:', cliente);

      // 2️⃣ Crear visita usando ESTADO GLOBAL
      const resVisita = await fetch('http://localhost:8000/visitas/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_cliente: cliente.id_cliente,
          id_barbero: barberoSeleccionado.id_barbero, // NO NULL
          id_servicio: servicioSeleccionado.id_servicio,
          fecha_hora: fechaHoraSeleccionada
        })
      });

      if (!resVisita.ok) {
        const err = await resVisita.json();
        throw new Error(err.detail || 'Error al crear visita');
      }

      const visita = await resVisita.json();
      console.log('Visita creada:', visita);

      alert('Turno agendado con éxito!');
      resetFlow();

    } catch (error) {
      console.error(error);
      alert(error.message);
    }
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

      {view === 'disponibilidad' && servicioSeleccionado && barberoSeleccionado && (
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
