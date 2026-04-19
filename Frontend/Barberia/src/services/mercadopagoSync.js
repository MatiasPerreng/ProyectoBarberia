import API_URL from "./api";
import { formatFastApiDetail, networkFailureMessage } from "../utils/apiError";

function apiBase() {
  return String(API_URL || "").replace(/\/+$/, "");
}

async function jsonBody(res) {
  return res.json().catch(() => ({}));
}

function errorFromSyncBody(data) {
  const detail = formatFastApiDetail(data);
  if (detail) return detail;
  return "No se pudo sincronizar con Mercado Pago.";
}

export function visitaDebeSincronizarMp(v) {
  if (!v) return false;
  const st = String(v.estado || "").toUpperCase();
  if (st !== "PENDIENTE_CONFIRMACION_MP") return false;
  if (v.mercadopago_payment_id || v.mercadopago_referencia) return false;
  if (v.mercadopago_receipt_url) return false;
  if (v.medio_pago && v.medio_pago !== "mercadopago") return false;
  return true;
}

export async function sincronizarPagoMercadoPagoPorVisita(idVisita) {
  let res;
  try {
    res = await fetch(`${apiBase()}/visitas/mercadopago/sincronizar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ external_reference: String(idVisita) }),
    });
  } catch (e) {
    return { ok: false, data: null, error: networkFailureMessage(e) };
  }
  const data = await jsonBody(res);
  if (!res.ok) {
    return { ok: false, data: null, error: errorFromSyncBody(data) };
  }
  return { ok: true, data, error: null };
}

export async function sincronizarPagoMercadoPagoPorVisitaConReintentos(idVisita) {
  const delays = [0, 2500, 5000];
  for (let i = 0; i < delays.length; i++) {
    if (delays[i]) await new Promise((r) => setTimeout(r, delays[i]));
    const r = await sincronizarPagoMercadoPagoPorVisita(idVisita);
    if (r.ok && (r.data?.mercadopago_payment_id || r.data?.mercadopago_referencia)) return r;
  }
  return sincronizarPagoMercadoPagoPorVisita(idVisita);
}

/** Mismo criterio que Burgers/PedidoPagoResultado: payment_id, external_reference, preference_id. */
export async function sincronizarVisitaMercadoPagoCompleto(syncBody) {
  let res;
  try {
    res = await fetch(`${apiBase()}/visitas/mercadopago/sincronizar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(syncBody),
    });
  } catch (e) {
    return { ok: false, data: null, error: networkFailureMessage(e) };
  }
  const data = await jsonBody(res);
  if (!res.ok) {
    return { ok: false, data: null, error: errorFromSyncBody(data) };
  }
  return { ok: true, data, error: null };
}

/** MP a veces indexa el pago unos segundos después: reintentos como en Burgers. */
export async function sincronizarVisitaMercadoPagoCompletoConReintentos(syncBody) {
  const delays = [0, 2000, 4500, 8000];
  for (let i = 0; i < delays.length; i++) {
    if (delays[i]) await new Promise((r) => setTimeout(r, delays[i]));
    const r = await sincronizarVisitaMercadoPagoCompleto(syncBody);
    if (r.ok && (r.data?.mercadopago_payment_id || r.data?.mercadopago_referencia)) {
      return r;
    }
  }
  return sincronizarVisitaMercadoPagoCompleto(syncBody);
}

export function mercadoPagoPaymentIdDesdeTexto(raw) {
  const s = String(raw ?? "").trim();
  if (!s) return null;
  if (/^\d+$/.test(s)) return s;
  const digits = s.replace(/\D/g, "");
  return digits.length >= 4 ? digits : null;
}

const DEFAULT_MP_RECEIPT_VIEW_HOST = "www.mercadopago.com.uy";

function mercadoPagoReceiptViewHost() {
  const v = import.meta.env.VITE_MERCADOPAGO_RECEIPT_VIEW_HOST;
  const s = v != null && String(v).trim() ? String(v).trim() : DEFAULT_MP_RECEIPT_VIEW_HOST;
  return s.replace(/^https?:\/\//, "").split("/")[0];
}

export function urlMercadoPagoReceiptViewPorOperacion(raw) {
  const id = mercadoPagoPaymentIdDesdeTexto(raw);
  if (!id) return null;
  const host = mercadoPagoReceiptViewHost();
  return `https://${host}/tools/receipt-view/${encodeURIComponent(id)}`;
}

export const MP_BROADCAST_NAME = "kingbarber-mp-visita";

const MP_SESSION_KEY = "kb_mp_agenda_pending_v1";
const MP_SESSION_MAX_AGE_MS = 24 * 60 * 60 * 1000;

export function mpPendingAgendaSave(visitaSnapshot, idVisita) {
  try {
    sessionStorage.setItem(
      MP_SESSION_KEY,
      JSON.stringify({
        visitaSnapshot,
        idVisita,
        phase: "checkout",
        startedAt: Date.now(),
      }),
    );
  } catch {
    /* */
  }
}

export function mpPendingAgendaClear() {
  try {
    sessionStorage.removeItem(MP_SESSION_KEY);
  } catch {
    /* */
  }
}

export function mpPendingAgendaLoad() {
  try {
    const raw = sessionStorage.getItem(MP_SESSION_KEY);
    if (!raw) return null;
    const p = JSON.parse(raw);
    const start = typeof p.startedAt === "number" ? p.startedAt : 0;
    if (!start || Date.now() - start > MP_SESSION_MAX_AGE_MS) {
      sessionStorage.removeItem(MP_SESSION_KEY);
      return null;
    }
    return p;
  } catch {
    return null;
  }
}
