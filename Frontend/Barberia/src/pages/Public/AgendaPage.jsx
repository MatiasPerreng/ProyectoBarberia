import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import ServiciosList from "../../components/ServiceList/ServiceList";
import BarberosList from "../../components/BarberoList/BarberoList";
import AgendaAvailability from "../../components/Agenda/AgendaAvailability/AgendaAvailability";
import AgendaForm from "../../components/Agenda/AgendaForm/AgendaForm";

import { crearCliente } from "../../services/clientes";
import { crearVisita } from "../../services/agenda";

export default function AgendaPage() {
  const location = useLocation();
  const navigate = useNavigate();

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

  // ----------------------------
  // HANDLERS DE PASOS
  // ----------------------------

  const handleServicioSelect = (servicio) => {
    setServicioSeleccionado(servicio);
    setView("barberos");
  };

  const handleBarberoSelect = (barbero) => {
    setBarberoSeleccionado(barbero);
    setFechaHoraSeleccionada(null);
    setView("disponibilidad");
  };

  const handleFechaHoraSelect = (fechaHora) => {
    setFechaHoraSeleccionada(fechaHora);
    setView("form");
  };

  // ----------------------------
  // 🔙 VOLVER AL HOME → SERVICIOS
  // ----------------------------

  const handleVolverDesdeBarberos = () => {
    // limpiar estado agenda
    setServicioSeleccionado(null);
    setBarberoSeleccionado(null);
    setFechaHoraSeleccionada(null);
    setView("servicios");

    // volver al home posicionado en servicios
    navigate("/", {
      replace: true,
      state: { focus: "servicios" }
    });
  };

  const handleVolverDesdeDisponibilidad = () => {
    setFechaHoraSeleccionada(null);
    setView("barberos");
  };

  const handleVolverDesdeForm = () => {
    setView("disponibilidad");
  };

  // ----------------------------
  // SUBMIT FINAL
  // ----------------------------

  const handleSubmitTurno = async (datosCliente) => {
    const restCliente = { ...datosCliente };
    const medio_pago = restCliente.medio_pago ?? "efectivo";
    delete restCliente.medio_pago;
    const cliente = await crearCliente(restCliente);

    const visita = await crearVisita({
      id_cliente: cliente.id_cliente,
      id_barbero: barberoSeleccionado?.id_barbero ?? null,
      id_servicio: servicioSeleccionado.id_servicio,
      fecha_hora: fechaHoraSeleccionada,
      medio_pago,
    });

    if (visita?.init_point) {
      return { skipSuccess: true, init_point: visita.init_point };
    }
    return { skipSuccess: false };
  };

  // ----------------------------
  // RENDER
  // ----------------------------

  return (
    <>
      {view === "servicios" && (
        <ServiciosList onSelectServicio={handleServicioSelect} />
      )}

      {view === "barberos" && (
        <BarberosList
          onSelectBarbero={handleBarberoSelect}
          onVolver={handleVolverDesdeBarberos}
        />
      )}

      {view === "disponibilidad" && (
        <AgendaAvailability
          servicio={servicioSeleccionado}
          barbero={barberoSeleccionado}
          onSelectFechaHora={handleFechaHoraSelect}
          onVolver={handleVolverDesdeDisponibilidad}
        />
      )}

      {view === "form" && (
        <AgendaForm
          onSubmit={handleSubmitTurno}
          onVolver={handleVolverDesdeForm}
          precioNeto={servicioSeleccionado?.precio}
        />
      )}
    </>
  );
}
