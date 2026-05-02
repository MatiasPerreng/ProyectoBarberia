import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import BarberoDaySummary from "../../components/Barbero/BarberoDaySummary";
import BarberoAgendaList from "../../components/Barbero/BarberoAgendaList/BarberoAgendaList";
import BarberoTurnoModal from "../../components/Barbero/BarberoTurnoModal";
import { getAgendaBarbero } from "../../services/barberos";
import "./BarberoDashboard.css";

/** Refresco en segundo plano (nuevas reservas / confirmación MP) sin recargar la página. */
const AGENDA_POLL_MS = 20_000;

const normalizarTurnosApi = (data) =>
  (Array.isArray(data) ? data : []).map((v) => ({
    id: v.id_visita,
    id_visita: v.id_visita,
    fecha_hora: v.fecha_hora,
    fechaHora: v.fecha_hora,

    hora: new Date(v.fecha_hora).toLocaleTimeString("es-UY", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }),

    cliente_nombre: v.cliente_nombre,
    cliente_apellido: v.cliente_apellido,
    telefono: v.cliente_telefono || "",

    servicio: v.servicio_nombre,
    servicio_nombre: v.servicio_nombre,
    duracion: v.servicio_duracion,
    servicio_duracion: v.servicio_duracion,

    estado: v.estado || "CONFIRMADO",
    precio: v.servicio_precio ?? v.precio ?? 0,
    servicio_precio: v.servicio_precio ?? v.precio ?? 0,

    medio_pago: v.medio_pago,
    mp_payment_id: v.mp_payment_id,
    comprobante_mp_url: v.comprobante_mp_url,
  }));

const BarberoDashboard = () => {
  const { pathname } = useLocation();
  const adminMiAgenda = pathname.includes("/admin/mi-agenda");

  const [fecha, setFecha] = useState(
    new Date().toISOString().split("T")[0]
  );

  const [turnos, setTurnos] = useState([]);
  const [turnoSeleccionado, setTurnoSeleccionado] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const fetchAgenda = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setLoading(true);
      try {
        const data = await getAgendaBarbero(fecha);
        if (!mounted.current) return;
        const normalizados = normalizarTurnosApi(data);
        setTurnos(normalizados);
        setTurnoSeleccionado((prev) => {
          if (!prev) return null;
          const id = prev.id ?? prev.id_visita;
          return (
            normalizados.find((t) => t.id === id || t.id_visita === id) ??
            prev
          );
        });
        setError(null);
      } catch {
        if (!mounted.current) return;
        if (!silent) setError("No se pudo cargar tu agenda");
      } finally {
        if (!mounted.current) return;
        if (!silent) setLoading(false);
      }
    },
    [fecha]
  );

  useEffect(() => {
    fetchAgenda({ silent: false });
  }, [fetchAgenda]);

  useEffect(() => {
    const id = setInterval(() => fetchAgenda({ silent: true }), AGENDA_POLL_MS);
    return () => clearInterval(id);
  }, [fetchAgenda]);

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState === "visible") fetchAgenda({ silent: true });
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [fetchAgenda]);

  const handleAtender = (id) => {
    setTurnos((prev) =>
      prev.map((t) =>
        t.id === id ? { ...t, estado: "completado" } : t
      )
    );
    setTurnoSeleccionado(null);
  };

  const handleCancelar = (id, motivo) => {
    setTurnos((prev) =>
      prev.map((t) =>
        t.id === id
          ? { ...t, estado: "cancelado", motivo }
          : t
      )
    );
    setTurnoSeleccionado(null);
  };

  if (loading) return <p>Cargando tu agenda…</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div
      className={`barbero-dashboard${adminMiAgenda ? " barbero-dashboard--admin-mi-agenda" : ""}`}
    >
      <h1>Mi agenda</h1>

      <BarberoDaySummary
        turnos={turnos}
        fecha={fecha}
        onChangeFecha={setFecha}
      />

      <BarberoAgendaList
        turnos={turnos}
        onSelectTurno={setTurnoSeleccionado}
      />

      {turnoSeleccionado && (
        <BarberoTurnoModal
          turno={turnoSeleccionado}
          onClose={() => setTurnoSeleccionado(null)}
          onAtender={handleAtender}
          onCancelar={handleCancelar}
        />
      )}
    </div>
  );
};

export default BarberoDashboard;
