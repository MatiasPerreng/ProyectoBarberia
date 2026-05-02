import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { sincronizarVisitaPagoMP, getVisitaSeguimiento } from "../../services/agenda";
import "./VisitaPagoResultado.css";

const titulos = {
  cargando: "Un momento…",
  ok: "Turno confirmado",
  fallo: "Reserva liberada",
  pendiente: "Pago en proceso",
  info: "Tu reserva",
  error: "No pudimos completar",
};

function IconOk() {
  return (
    <svg className="vpr-icon-svg" viewBox="0 0 48 48" aria-hidden>
      <circle cx="24" cy="24" r="22" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.35" />
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M14 24l7 7 13-14"
      />
    </svg>
  );
}

function IconPending() {
  return (
    <svg className="vpr-icon-svg" viewBox="0 0 48 48" aria-hidden>
      <circle cx="24" cy="24" r="20" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.35" />
      <path
        d="M24 14v10l6 4"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconWarn() {
  return (
    <svg className="vpr-icon-svg" viewBox="0 0 48 48" aria-hidden>
      <circle cx="24" cy="24" r="20" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.35" />
      <path
        fill="currentColor"
        d="M24 15a1.5 1.5 0 011.5 1.5v10a1.5 1.5 0 01-3 0v-10A1.5 1.5 0 0124 15zm0 16.5a2 2 0 100 4 2 2 0 000-4z"
      />
    </svg>
  );
}

function IconSpinner() {
  return (
    <svg className="vpr-icon-svg vpr-icon-svg--spin" viewBox="0 0 48 48" aria-hidden>
      <circle
        cx="24"
        cy="24"
        r="20"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeDasharray="90 120"
        opacity="0.9"
      />
    </svg>
  );
}

export default function VisitaPagoResultado() {
  const [params] = useSearchParams();
  const [estado, setEstado] = useState("cargando");
  const [mensaje, setMensaje] = useState("");
  const [detalle, setDetalle] = useState(null);

  useEffect(() => {
    const token = params.get("token");
    const paymentId = params.get("payment_id") || params.get("collection_id");

    if (!token) {
      setEstado("error");
      setMensaje("Falta el token de seguimiento en la URL.");
      return;
    }

    (async () => {
      try {
        if (paymentId) {
          const v = await sincronizarVisitaPagoMP(token, paymentId);
          setDetalle(v);
          if (v.estado === "CONFIRMADO") {
            setEstado("ok");
            setMensaje("¡Pago acreditado! Tu turno quedó confirmado.");
          } else if (v.estado === "CANCELADO") {
            setEstado("fallo");
            setMensaje("El pago no se completó. El turno fue liberado.");
          } else {
            setEstado("pendiente");
            setMensaje("El pago está pendiente de confirmación. Podés volver más tarde o contactarnos.");
          }
        } else {
          const v = await getVisitaSeguimiento(token);
          setDetalle(v);
          setEstado("info");
          setMensaje(
            v.estado === "CONFIRMADO"
              ? "Tu turno ya está confirmado."
              : v.estado === "PENDIENTE_CONFIRMACION_MP"
                ? "Seguimos esperando la confirmación del pago."
                : `Estado del turno: ${v.estado || "—"}`
          );
        }
      } catch (e) {
        setEstado("error");
        setMensaje(e?.message || "No se pudo actualizar el estado del pago.");
      }
    })();
  }, [params]);

  let titulo = titulos[estado] || titulos.info;
  if (estado === "info" && detalle?.estado === "CONFIRMADO") titulo = "Turno confirmado";
  if (estado === "info" && detalle?.estado === "PENDIENTE_CONFIRMACION_MP") titulo = "Pago en proceso";

  const textoPrincipal = estado === "cargando" && !mensaje ? "Consultamos el estado de tu pago…" : mensaje;

  const fechaFormateada = useMemo(() => {
    if (!detalle?.fecha_hora) return null;
    try {
      return new Date(detalle.fecha_hora).toLocaleString("es-UY", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return String(detalle.fecha_hora);
    }
  }, [detalle?.fecha_hora]);

  const icono = (() => {
    if (estado === "cargando") return <IconSpinner />;
    if (estado === "ok") return <IconOk />;
    if (estado === "pendiente" || estado === "info") return <IconPending />;
    return <IconWarn />;
  })();

  return (
    <div className="vpr-wrap">
      <div className={`vpr-card vpr-card--${estado}`}>
        <div className="vpr-card__inner">
          <div className="vpr-brand">
            <img src="/logo.jpg" alt="King Barber" className="vpr-brand__logo" width={72} height={72} />
            <span className="vpr-brand__name">King Barber</span>
          </div>

          <div className={`vpr-icon-wrap vpr-icon-wrap--${estado}`}>{icono}</div>

          <h1 className="vpr-title">{titulo}</h1>
          <p className="vpr-msg">{textoPrincipal}</p>

          {detalle?.fecha_hora && (
            <div className="vpr-details">
              <span className="vpr-details__kicker">Tu turno</span>
              <p className="vpr-details__fecha">{fechaFormateada}</p>
              {detalle.servicio_nombre && (
                <p className="vpr-details__servicio">{detalle.servicio_nombre}</p>
              )}
            </div>
          )}

          {detalle?.comprobante_mp_url &&
            estado !== "cargando" &&
            estado !== "error" &&
            estado !== "fallo" && (
            <a
              href={detalle.comprobante_mp_url}
              target="_blank"
              rel="noopener noreferrer"
              className="vpr-comp"
            >
              <img className="vpr-comp__logo" src="/mercadopago.png" alt="" />
              Ver comprobante Mercado Pago
            </a>
          )}

          <div className="vpr-actions">
            <Link to="/" className="vpr-btn-home">
              Volver al inicio
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
