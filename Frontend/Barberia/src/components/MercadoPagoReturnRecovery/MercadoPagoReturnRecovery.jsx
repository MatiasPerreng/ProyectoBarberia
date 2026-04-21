import { useEffect, useRef } from "react";
import {
  mpPendingAgendaLoad,
  mpPendingAgendaClear,
  sincronizarPagoMercadoPagoPorVisitaConReintentos,
} from "../../services/mercadopagoSync";

/**
 * Si el usuario volvió de Mercado Pago a una URL distinta de /agenda/pago-resultado
 * (o MP no agregó query params), igual intentamos confirmar el pago con el id_visita guardado.
 */
export default function MercadoPagoReturnRecovery() {
  const attempted = useRef(false);

  useEffect(() => {
    if (attempted.current) return;
    const pend = mpPendingAgendaLoad();
    if (!pend?.readyForReturnSync || pend.idVisita == null) return;
    attempted.current = true;

    let cancelled = false;
    (async () => {
      const r = await sincronizarPagoMercadoPagoPorVisitaConReintentos(pend.idVisita);
      if (cancelled) return;
      if (r.ok && r.data?.mercadopago_payment_id) {
        mpPendingAgendaClear();
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  return null;
}
