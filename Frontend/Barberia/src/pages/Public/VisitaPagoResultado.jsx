import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { sincronizarVisitaPagoMP, getVisitaSeguimiento } from "../../services/agenda";
import "./VisitaPagoResultado.css";

/** Solo dígitos (ej. 59899611465). Mostramos 099 611 465 en pantalla. */
const WA_MSISDN =
  (import.meta.env.VITE_WHATSAPP_TURNO || "59899611465").replace(/\D/g, "") || "59899611465";
const WA_HREF = `https://wa.me/${WA_MSISDN}`;
const WA_TEL_LABEL = import.meta.env.VITE_WHATSAPP_TURNO_LABEL?.trim() || "099 611 465";

const MP_REEMBOLSO_HREF =
  import.meta.env.VITE_MP_REEMBOLSO_URL?.trim() || "https://www.mercadopago.com.uy/ayuda";

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

/** Triángulo de alerta rojo (esquinas redondeadas, borde oscuro, ! blanco). */
function IconAlertFallo() {
  return (
    <svg className="vpr-icon-fallo" viewBox="-2 -2 68 68" aria-hidden focusable="false">
      <polygon
        points="32,12.5 53.5,51.5 10.5,51.5"
        fill="#ef4444"
        stroke="#991b1b"
        strokeWidth="3.2"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <path
        d="M32 25.5v12.5"
        stroke="#ffffff"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <circle cx="32" cy="46.5" r="3.2" fill="#ffffff" />
    </svg>
  );
}

function IconWhatsApp({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden focusable="false">
      <path
        fill="currentColor"
        d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"
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
            setMensaje("");
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
    if (estado === "fallo") return <IconAlertFallo />;
    return <IconWarn />;
  })();

  return (
    <div className="vpr-wrap">
      <div className={`vpr-card vpr-card--${estado}`}>
        <div className="vpr-card__inner">
          <div className="vpr-brand">
            <img
              src="/logo.jpg"
              alt="King Barber"
              className={`vpr-brand__logo${estado === "fallo" ? " vpr-brand__logo--fallo" : ""}`}
              width={72}
              height={72}
            />
            <span className={`vpr-brand__name${estado === "fallo" ? " vpr-brand__name--fallo" : ""}`}>
              King Barber
            </span>
          </div>

          <div className={`vpr-icon-wrap vpr-icon-wrap--${estado}`}>{icono}</div>

          <h1 className={`vpr-title${estado === "fallo" ? " vpr-title--fallo" : ""}`}>{titulo}</h1>
          {estado === "fallo" ? (
            <div className="vpr-msg vpr-msg--fallo">
              <p className="vpr-msg--fallo__lead">
                Tardaste en realizar el pago y tu horario pudo haber sido tomado por otro cliente.
              </p>
              <p className="vpr-msg--fallo__hint">
                Escribinos por WhatsApp o pedí reembolso en Mercado Pago si ya te debitaron.
              </p>
              <div className="vpr-msg--fallo__acciones">
                <a
                  href={WA_HREF}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="vpr-fallo-link vpr-fallo-link--wa"
                >
                  <IconWhatsApp className="vpr-fallo-wa-ico" />
                  <span>{WA_TEL_LABEL}</span>
                </a>
                <a
                  href={MP_REEMBOLSO_HREF}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="vpr-fallo-link vpr-fallo-link--mp"
                >
                  Solicitar reembolso
                </a>
              </div>
            </div>
          ) : (
            <p className="vpr-msg">{textoPrincipal}</p>
          )}

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
              className="kb-mp-comprobante kb-mp-comprobante--vpr"
            >
              <img className="kb-mp-comprobante__logo" src="/mercadopago.png" alt="" />
              <span className="kb-mp-comprobante__text">ver comprobante</span>
            </a>
          )}

          <div className="vpr-actions">
            <Link to="/" className={estado === "fallo" ? "vpr-btn-home vpr-btn-home--compact" : "vpr-btn-home"}>
              Volver al inicio
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
