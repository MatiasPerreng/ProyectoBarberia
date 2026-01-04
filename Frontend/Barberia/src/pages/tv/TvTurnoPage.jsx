import { useEffect, useState, useRef } from "react";
import "./TvTurnoPage.css";
import API_URL from "../../services/api";

export default function TvAgendaPage() {
  const [enCurso, setEnCurso] = useState([]);
  const [proximos, setProximos] = useState([]);
  const [indiceProximo, setIndiceProximo] = useState(0);
  const [horaActual, setHoraActual] = useState("");
  const [minuteTick, setMinuteTick] = useState(false);

  const lastMinuteRef = useRef(null);

  useEffect(() => {
    const actualizarHora = () => {
      const now = new Date();
      const horaStr = now.toLocaleTimeString("es-UY", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });

      const minuto = now.getMinutes();
      if (
        lastMinuteRef.current !== null &&
        minuto !== lastMinuteRef.current
      ) {
        setMinuteTick(true);
        setTimeout(() => setMinuteTick(false), 400);
      }

      lastMinuteRef.current = minuto;
      setHoraActual(horaStr);
    };

    actualizarHora();
    const reloj = setInterval(actualizarHora, 1000);
    return () => clearInterval(reloj);
  }, []);

  useEffect(() => {
    cargarAgenda();
    const interval = setInterval(cargarAgenda, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (proximos.length === 0) return;

    const rotador = setInterval(() => {
      setIndiceProximo((prev) => (prev + 1) % proximos.length);
    }, 5000);

    return () => clearInterval(rotador);
  }, [proximos]);

  const cargarAgenda = async () => {
    try {
      const res = await fetch(`${API_URL}/tv/agenda-estado`);
      const data = await res.json();
      setEnCurso(data.en_curso || []);
      setProximos(data.proximos || []);
      setIndiceProximo(0);
    } catch (err) {
      console.error("Error cargando TV agenda", err);
    }
  };

  const proximo = proximos[indiceProximo];

  return (
    <div className="tv-agenda-container tv-43">
      <header className="tv-header">
        <div className="tv-brand">
          <img src="/logo.jpg" alt="King Barber" className="tv-logo" />
          <span className="tv-brand-text">KING BARBER</span>
        </div>

        <div className={`tv-clock ${minuteTick ? "minute-tick" : ""}`}>
          {horaActual}
        </div>
      </header>

      <main className="tv-main-content">
        {/* ===================== EN CURSO ===================== */}
        <section className="tv-section">
          <div className="tv-section-header">
            <h2 className="tv-title">SERVICIOS EN CURSO</h2>
            <div className="live-badge">EN VIVO</div>
          </div>

          <div className="tv-list">
            {enCurso.length === 0 ? (
              <p className="tv-muted">No hay servicios activos</p>
            ) : (
              enCurso.slice(0, 2).map((s, i) => (
                <div key={i} className="tv-item">
                  <div className="tv-barbero-col">
                    <span className="tv-label">BARBERO</span>
                    <div className="tv-barbero">{s.barbero}</div>
                  </div>

                  <div className="tv-info-col">
                    <div className="tv-servicio">{s.servicio}</div>
                    <div className="tv-cliente">{s.cliente}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* ===================== PRÓXIMO ===================== */}
        <section className="tv-section next">
          <h2 className="tv-title gold">PRÓXIMO SERVICIO</h2>

          {proximo ? (
            <div key={indiceProximo} className="tv-next-card tv-animate">
              <div className="tv-next-hora">{proximo.hora}</div>

              <div className="tv-next-details">
                <span className="tv-next-serv">{proximo.servicio}</span>
                <span className="tv-sep">|</span>
                <span className="tv-next-cli">{proximo.cliente}</span>
              </div>

              <div className="tv-next-barbero">
                con <strong>{proximo.barbero}</strong>
              </div>

              <div className="shimmer-effect" />
            </div>
          ) : (
            <p className="tv-muted">Agenda completa</p>
          )}
        </section>
      </main>

      <footer className="tv-footer">
        DESARROLLADO POR <strong>MATIAS PERRENG</strong>
      </footer>
    </div>
  );
}
