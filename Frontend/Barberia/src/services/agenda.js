import API_URL from "./api";

/* =========================
   CREAR VISITA
========================= */
function detalleErrorApi(err) {
  const d = err?.detail;
  if (Array.isArray(d)) {
    return d.map((x) => x.msg || JSON.stringify(x)).join("; ");
  }
  if (typeof d === "string") return d;
  return err?.message || "Error al crear visita";
}

export async function crearVisita(data) {
  const res = await fetch(`${API_URL}/visitas/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(detalleErrorApi(body));
  }

  return body;
}

export async function sincronizarVisitaPagoMP(token, paymentId) {
  const q = new URLSearchParams({ token, payment_id: String(paymentId) });
  const res = await fetch(`${API_URL}/visitas/seguimiento/sincronizar?${q.toString()}`, {
    method: "GET",
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(detalleErrorApi(body));
  }
  return body;
}

export async function getVisitaSeguimiento(token) {
  const res = await fetch(`${API_URL}/visitas/seguimiento/${encodeURIComponent(token)}`);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(detalleErrorApi(body));
  }
  return body;
}

/* =========================
   AGENDA BARBERO
========================= */
export async function getAgendaBarbero(idBarbero) {
  const res = await fetch(`${API_URL}/barberos/${idBarbero}/agenda`);

  if (!res.ok) {
    throw new Error("Error al cargar agenda");
  }

  return await res.json();
}

/* =========================
   DISPONIBILIDAD
========================= */
export async function getDisponibilidad({
  fecha,
  id_servicio,
  id_barbero,
}) {
  let url = `${API_URL}/visitas/disponibilidad?fecha=${fecha}&id_servicio=${id_servicio}`;

  if (id_barbero) {
    url += `&id_barbero=${id_barbero}`;
  }

  const res = await fetch(url);

  if (!res.ok) {
    throw new Error("Error al cargar disponibilidad");
  }

  return await res.json();
}



export async function getDisponibilidadMes({
  mes,
  anio,
  id_servicio,
  id_barbero,
}) {
  const res = await fetch(
    `${API_URL}/visitas/disponibilidad-mes?mes=${mes}&anio=${anio}&id_servicio=${id_servicio}&id_barbero=${id_barbero}`
  );

  if (!res.ok) {
    throw new Error("Error al cargar disponibilidad mensual");
  }

  return await res.json();
}