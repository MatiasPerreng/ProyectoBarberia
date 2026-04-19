import { apiFetch } from "./apiClient";

export async function getAdminDashboard() {
  const res = await apiFetch("/admin/dashboard", { cache: "no-store" });

  if (!res.ok) {
    throw new Error("Error al cargar dashboard");
  }

  return await res.json();
}

/** IDs de visitas MP sin n° de operación (polling admin, mismo criterio que Burgers). */
export async function getAdminMpVisitasPendientesSync() {
  const res = await apiFetch("/admin/mercadopago/visitas-pendientes-sync", {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("No se pudo consultar pagos pendientes");
  }
  return res.json();
}
