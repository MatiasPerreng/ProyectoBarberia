import { useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

import ServiciosList from "../../components/ServiceList/ServiceList";
import BarberosList from "../../components/BarberoList/BarberoList";
import AgendaAvailability from "../../components/Agenda/AgendaAvailability/AgendaAvailability";
import AgendaForm from "../../components/Agenda/AgendaForm/AgendaForm";

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


  const handleSubmitTurno = async (datosCliente) => {
    const cliente = await crearCliente(datosCliente);

    await crearVisita({
      id_cliente: cliente.id_cliente,
      id_barbero: barberoSeleccionado?.id_barbero ?? null,
      id_servicio: servicioSeleccionado.id_servicio,
      fecha_hora: fechaHoraSeleccionada,
    });

    return true;
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
