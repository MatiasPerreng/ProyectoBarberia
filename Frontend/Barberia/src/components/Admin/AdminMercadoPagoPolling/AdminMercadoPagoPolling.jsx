import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { getAdminMpVisitasPendientesSync } from "../../../services/dashboard";
import { sincronizarPagoMercadoPagoPorVisitaConReintentos } from "../../../services/mercadopagoSync";

/** Igual que antes en AdminDashboard: ~25 s. Corre en cualquier ruta /admin/*. */
const MP_ADMIN_SYNC_MS = 25_000;

const EVENT_REFRESH = "kb-admin-dashboard-refresh";

/**
 * Polling de pagos MP pendientes mientras hay sesión admin.
 * Debe vivir en AdminLayout (no en AdminDashboard): si no, al ir a /admin/mi-agenda
 * se desmonta el dashboard y deja de llamarse /admin/mercadopago/visitas-pendientes-sync.
 */
export default function AdminMercadoPagoPolling() {
  const location = useLocation();

  useEffect(() => {
    if (!location.pathname.startsWith("/admin")) return;

    const runSync = () => {
      void (async () => {
        let huboOk = false;
        try {
          const { ids } = await getAdminMpVisitasPendientesSync();
          if (!Array.isArray(ids) || !ids.length) return;
          for (const idVisita of ids) {
            const r = await sincronizarPagoMercadoPagoPorVisitaConReintentos(idVisita);
            if (r.ok && (r.data?.mercadopago_payment_id || r.data?.mercadopago_referencia)) {
              huboOk = true;
            }
          }
        } catch {
          /* red o backend */
        }
        if (huboOk) {
          window.dispatchEvent(new CustomEvent(EVENT_REFRESH));
        }
      })();
    };

    runSync();
    const id = setInterval(runSync, MP_ADMIN_SYNC_MS);
    return () => clearInterval(id);
  }, [location.pathname]);

  return null;
}
