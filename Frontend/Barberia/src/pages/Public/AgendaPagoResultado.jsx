import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import MercadoPagoComprobanteLink from "../../components/MercadoPagoComprobanteLink/MercadoPagoComprobanteLink";
import {
  MP_BROADCAST_NAME,
  mpPendingAgendaClear,
  mpPendingAgendaLoad,
  sincronizarVisitaMercadoPagoCompletoConReintentos,
} from "../../services/mercadopagoSync";
import "./AgendaPagoResultado.css";

function apiBase() {
  const raw = String(API_URL || "").replace(/\/+$/, "");
  return raw || "/api";
}

function mergeSearchAndHash(location) {
  const merged = new URLSearchParams(location.search);
  const h = location.hash;
  if (h && h.length > 1) {
    const raw = h.startsWith("#") ? h.slice(1) : h;
    if (raw.includes("=")) {
      const queryPart = raw.includes("?") ? raw.split("?").slice(1).join("?") : raw;
      const hp = new URLSearchParams(queryPart);
      hp.forEach((value, key) => {
        if (!merged.has(key)) merged.set(key, value);
      });
    }
  }
  return merged;
}

export default function AgendaPagoResultado() {
  const location = useLocation();
  const params = useMemo(() => mergeSearchAndHash(location), [location.search, location.hash]);
  const [state, setState] = useState({ loading: true, error: null, visita: null });
  const broadcastHecho = useRef(false);

  useEffect(() => {
    const v = state.visita;
    if (!v || broadcastHecho.current) return;
    if (!v.mercadopago_payment_id) return;
    broadcastHecho.current = true;
    try {
      const bc = new BroadcastChannel(MP_BROADCAST_NAME);
      bc.postMessage({ type: "paid", visita: v });
      bc.close();
    } catch {
      /* */
    }
  }, [state.visita]);

  useEffect(() => {
    const collectionStatus = params.get("collection_status");
    const st = params.get("status");

    if (collectionStatus === "null" || st === "null") {
      setState({
        loading: false,
        error: "No se completó el pago en Mercado Pago.",
        visita: null,
      });
      return;
    }

    if (collectionStatus === "rejected" || st === "rejected") {
      setState({
        loading: false,
        error: "El pago fue rechazado. Podés volver a la agenda e intentar de nuevo.",
        visita: null,
      });
      return;
    }

    const paymentId = params.get("payment_id") || params.get("collection_id");
    const extRef = params.get("external_reference");
    const prefId = params.get("preference_id");
    const pend = mpPendingAgendaLoad();
    const extFromSession = pend?.idVisita != null ? String(pend.idVisita) : null;

    if (!paymentId && !extRef && !prefId && !extFromSession) {
      setState({
        loading: false,
        error:
          "No se recibieron datos del pago en la URL. Si ya pagaste, esperá unos segundos y recargá esta página.",
        visita: null,
      });
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const syncBody = {};
        if (paymentId) syncBody.payment_id = paymentId;
        if (extRef) syncBody.external_reference = extRef;
        else if (extFromSession) syncBody.external_reference = extFromSession;
        if (prefId) syncBody.preference_id = prefId;

        const { ok, data, error } = await sincronizarVisitaMercadoPagoCompletoConReintentos(syncBody);
        if (cancelled) return;
        if (!ok) {
          throw new Error(error || "No se pudo confirmar el pago.");
        }
        mpPendingAgendaClear();
        setState({ loading: false, error: null, visita: data });
      } catch (e) {
        if (!cancelled) {
          setState({
            loading: false,
            error: e.message || "Error al sincronizar",
            visita: null,
          });
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [params]);

  return (
    <div className="agenda-mp-page">
      <main className="agenda-mp-main">
        <div className="agenda-mp-card">
          <h1 className="agenda-mp-title">Pago — Mercado Pago</h1>

          {state.loading && <p className="agenda-mp-sub">Confirmando con el servidor…</p>}

          {!state.loading && state.error && (
            <div className="agenda-mp-alert agenda-mp-alert--warn" role="status">
              <p className="mb-2">{state.error}</p>
              <Link to="/agenda" className="agenda-mp-link">
                Volver a la agenda
              </Link>
            </div>
          )}

          {!state.loading && state.visita && (
            <div className="agenda-mp-alert agenda-mp-alert--ok" role="status">
              <p className="mb-2">
                Turno <strong>#{state.visita.id_visita}</strong> · Estado:{" "}
                <strong>{state.visita.estado}</strong>
              </p>
              {state.visita.mercadopago_payment_id && (
                <p className="agenda-mp-comp mb-2">
                  <MercadoPagoComprobanteLink paymentId={state.visita.mercadopago_payment_id} />
                </p>
              )}
              {state.visita.mercadopago_receipt_url &&
                !state.visita.mercadopago_payment_id && (
                  <p className="small mb-2">
                    <a href={state.visita.mercadopago_receipt_url} target="_blank" rel="noopener noreferrer">
                      Ver comprobante (PDF)
                    </a>
                  </p>
                )}
              <p className="small mb-0">
                <Link to="/">Ir al inicio</Link>
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
