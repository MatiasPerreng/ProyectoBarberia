import { useState } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Lobby from './Lobby/Lobby';
import ServiciosList from './ServiceList/ServiceList';
import AgendaForm from './AgendaForm/AgendaForm';

function App() {
  const [view, setView] = useState('lobby'); // 'lobby' | 'servicios' | 'form'
  const [servicioSeleccionado, setServicioSeleccionado] = useState(null);

  const handleAgendaClick = () => {
    setView('servicios'); // mostrar lista de servicios
  };

  const handleServicioSelect = (servicio) => {
    setServicioSeleccionado(null);  // limpiar primero
    setTimeout(() => setServicioSeleccionado(servicio), 0); // luego setear servicio
    setView('form');
  };

  const handleSubmitTurno = (turno) => {
    // Llamada al backend para crear cliente/turno
    fetch('http://localhost:8000/clientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(turno),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log('Turno agendado', data);
        alert('Turno agendado con éxito!');
        setServicioSeleccionado(null); // limpiar
        setView('lobby'); // volver al lobby
      })
      .catch((err) => console.error(err));
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
