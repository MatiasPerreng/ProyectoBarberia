import API_URL from "./api";
import { formatFastApiDetail, networkFailureMessage } from "../utils/apiError";

async function jsonBody(res) {
  return res.json().catch(() => ({}));
}

/* =========================
   CREAR VISITA
========================= */
export async function crearVisita(data) {
  let res;
  try {
    res = await fetch(`${API_URL}/visitas/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
  } catch (e) {
    throw new Error(networkFailureMessage(e));
  }

  const err = await jsonBody(res);
  if (!res.ok) {
    throw new Error(formatFastApiDetail(err) || "Error al crear visita");
  }

  return err;
}

/* =========================
   AGENDA BARBERO
========================= */
export async function getAgendaBarbero(idBarbero) {
  let res;
  try {
    res = await fetch(`${API_URL}/barberos/${idBarbero}/agenda`);
  } catch (e) {
    throw new Error(networkFailureMessage(e));
  }

  if (!res.ok) {
    const err = await jsonBody(res);
    throw new Error(formatFastApiDetail(err) || "Error al cargar agenda");
  }

  return res.json();
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

  let res;
  try {
    res = await fetch(url);
  } catch (e) {
    throw new Error(networkFailureMessage(e));
  }

  if (!res.ok) {
    const err = await jsonBody(res);
    throw new Error(formatFastApiDetail(err) || "Error al cargar disponibilidad");
  }

  return res.json();
}

export async function getDisponibilidadMes({
  mes,
  anio,
  id_servicio,
  id_barbero,
}) {
  let res;
  try {
    res = await fetch(
      `${API_URL}/visitas/disponibilidad-mes?mes=${mes}&anio=${anio}&id_servicio=${id_servicio}&id_barbero=${id_barbero}`
    );
  } catch (e) {
    throw new Error(networkFailureMessage(e));
  }

  if (!res.ok) {
    const err = await jsonBody(res);
    throw new Error(formatFastApiDetail(err) || "Error al cargar disponibilidad mensual");
  }

  return res.json();
}
