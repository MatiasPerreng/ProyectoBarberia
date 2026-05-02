import { useCallback, useEffect, useRef, useState } from "react";
import BarberoAgendaList from "../../components/Barbero/BarberoAgendaList/BarberoAgendaList";
import BarberoDaySummary from "../../components/Barbero/BarberoDaySummary";
import API_URL from "../../services/api";
import "./BarberAgenda.css";

const AGENDA_POLL_MS = 20_000;

const BarberAgenda = () => {
  // 📅 Día seleccionado (por defecto HOY)
  const [fecha, setFecha] = useState(() =>
    new Date().toISOString().split("T")[0]
  );

  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);
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
      const q = fecha ? `?fecha=${encodeURIComponent(fecha)}` : "";
      try {
        const res = await fetch(`${API_URL}/visitas/mi-agenda${q}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        const data = await res.json();
        if (!mounted.current) return;
        if (res.ok) setTurnos(Array.isArray(data) ? data : []);
        else if (!silent) setTurnos([]);
      } catch {
        if (!mounted.current) return;
        if (!silent) setTurnos([]);
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

  return (
    <div className="barbero-agenda-page">
      <h1>Mi agenda</h1>

      {/* =========================
         RESUMEN + FILTRO (COMPONENTE CORRECTO)
      ========================= */}
      <BarberoDaySummary
        turnos={turnos}
        fecha={fecha}
        onChangeFecha={setFecha}
      />

      {/* =========================
         LISTADO
      ========================= */}
      {loading && <p>Cargando agenda…</p>}

      {!loading && turnos.length === 0 && (
        <p className="agenda-empty">
          No tenés turnos para este día
        </p>
      )}

      {!loading && turnos.length > 0 && (
        <BarberoAgendaList
          turnos={turnos}
          onSelectTurno={() => { }}
        />
      )}
    </div>
  );
};

export default BarberAgenda;
