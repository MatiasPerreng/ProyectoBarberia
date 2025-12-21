import { useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

import ServiciosList from "../../components/ServiceList/ServiceList";
import BarberosList from "../../components/BarberoList/BarberoList";
import AgendaAvailability from "../../components/Agenda/AgendaAvailability";
import AgendaForm from "../../components/Agenda/AgendaForm";

import { crearCliente } from "../../services/clientes";
import { crearVisita } from "../../services/agenda";

export default function AgendaPage() {
  const location = useLocation();

  const [view, setView] = useState("servicios");

  const [servicioSeleccionado, setServicioSeleccionado] = useState(null);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);
  const [fechaHoraSeleccionada, setFechaHoraSeleccionada] = useState(null);

  // 👉 si viene desde Home con servicio ya elegido
  useEffect(() => {
    if (location.state?.servicio) {
      setServicioSeleccionado(location.state.servicio);
      setView("barberos");
    }
  }, [location.state]);

  const handleServicioSelect = (servicio) => {
    setServicioSeleccionado(servicio);
    setView("barberos");
  };

  const handleBarberoSelect = (barbero) => {
    setBarberoSeleccionado(barbero);
    setView("disponibilidad");
  };

  const handleFechaHoraSelect = (fechaHora) => {
    setFechaHoraSeleccionada(fechaHora);
    setView("form");
  };

  const resetFlow = () => {
    setServicioSeleccionado(null);
    setBarberoSeleccionado(null);
    setFechaHoraSeleccionada(null);
    setView("servicios");
  };

  const handleSubmitTurno = async (datosCliente) => {
    try {
      const cliente = await crearCliente(datosCliente);

      await crearVisita({
        id_cliente: cliente.id_cliente,
        id_barbero: barberoSeleccionado?.id_barbero ?? null,
        id_servicio: servicioSeleccionado.id_servicio,
        fecha_hora: fechaHoraSeleccionada,
      });

      alert("Turno agendado con éxito!");
      resetFlow();
    } catch (error) {
      console.error(error);
      alert(error.message || "Error al agendar turno");
    }
  };

  return (
    <>
      {view === "servicios" && (
        <ServiciosList onSelectServicio={handleServicioSelect} />
      )}

      {view === "barberos" && (
        <BarberosList onSelectBarbero={handleBarberoSelect} />
      )}

      {view === "disponibilidad" && (
        <AgendaAvailability
          servicio={servicioSeleccionado}
          barbero={barberoSeleccionado}
          onSelectFechaHora={handleFechaHoraSelect}
        />
      )}

      {view === "form" && (
        <AgendaForm onSubmit={handleSubmitTurno} />
      )}
    </>
  );
}
