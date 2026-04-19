/**
 * Normaliza `detail` de respuestas FastAPI (string, array de validación, u objeto).
 */
export function formatFastApiDetail(body) {
  if (body == null || typeof body !== "object") return null;
  const d = body.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((x) => (x && typeof x === "object" && "msg" in x ? x.msg : String(x)))
      .join(" ")
      .trim();
  }
  if (d != null && typeof d === "object" && "message" in d) {
    return String(d.message);
  }
  return null;
}

/** Mensaje cuando `fetch` falla (red, CORS, servidor caído). */
export function networkFailureMessage(err) {
  if (err && err.name === "AbortError") {
    return "La solicitud fue cancelada.";
  }
  return "No se pudo conectar con el servidor. Comprobá tu conexión e intentá de nuevo.";
}

export function isLikelyNetworkError(err) {
  return (
    err instanceof TypeError ||
    (err && err.name === "AbortError") ||
    (typeof navigator !== "undefined" && !navigator.onLine)
  );
}
