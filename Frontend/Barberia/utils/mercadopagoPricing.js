/** Mismas constantes que Backend/utils/mercadopago_pricing.py */
export const MP_COMISION_BASE = 0.0499;
export const MP_IVA_SOBRE_COMISION = 1.22;
export const MP_TASA_TOTAL_EFECTIVA = MP_COMISION_BASE * MP_IVA_SOBRE_COMISION;
export const MP_DIVISOR_NETO = 1 - MP_TASA_TOTAL_EFECTIVA;

/**
 * @param {number|string} precioNeto
 * @returns {{ precioFinal: number, montoExtra: number }}
 */
export function calcularPrecioMercadoPago(precioNeto) {
  const neto = Number(precioNeto);
  if (Number.isNaN(neto) || neto < 0) {
    throw new Error("precio_neto no puede ser negativo");
  }
  if (neto === 0) {
    return { precioFinal: 0, montoExtra: 0 };
  }
  const precioFinal = Math.round((neto / MP_DIVISOR_NETO) * 100) / 100;
  const montoExtra = Math.round((precioFinal - neto) * 100) / 100;
  return { precioFinal, montoExtra };
}

export function formatearPesosUY(monto) {
  return new Intl.NumberFormat("es-UY", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(monto) || 0);
}
