# Mercado Pago — precio neto vs precio final (comisión absorbida por el cliente)

## Objetivo de negocio

En la base de datos, el **precio del servicio es neto**: es lo que debe recibir el barbero (ej. $350).

Si el cliente paga con **Mercado Pago**, MP descuenta:

1. Comisión base: **4,99%** (`0.0499`)
2. IVA uruguayo sobre esa comisión: **22%** → factor **1,22**

Para que, después de esos descuentos, al barbero le quede exactamente el precio neto del servicio, el **cliente paga un monto mayor** (precio bruto / final).

---

## Fórmula

```
tasa_total_efectiva = 0.0499 × 1.22 = 0.060878  (6,0878 %)
divisor_neto        = 1 - 0.060878 = 0.939122

precio_final = precio_neto / 0.939122
monto_extra  = precio_final - precio_neto   (redondeado a 2 decimales)
```

**Ejemplo:** `precio_neto = 350` → `precio_final = 372,69`, `monto_extra = 22,69`.

La fórmula aplica a **cualquier** precio neto positivo; el redondeo a 2 decimales puede generar diferencias de hasta ~$0,01 en el neto recuperado.

---

## Implementación en el repo

### Backend (fuente de verdad para Checkout Pro)

| Archivo | Rol |
|---------|-----|
| `Backend/utils/mercadopago_pricing.py` | Constantes MP + `calcular_precio_mercadopago(precio_neto)` → `PrecioMercadoPago(precio_final, monto_extra)` |
| `Backend/crud/visita.py` | Al crear preferencia MP: `unit_price = calcular_precio_mercadopago(precio_neto).precio_final` |
| `Backend/crud/visita.py` | `_mp_precio_esperado_uyu()` usa el mismo bruto para validar `transaction_amount` del webhook |

Atajo: `precio_final_mercadopago(precio_neto)` devuelve solo el bruto.

### Frontend (preview + aviso al usuario)

| Archivo | Rol |
|---------|-----|
| `Frontend/Barberia/utils/mercadopagoPricing.js` | Mismas constantes y `calcularPrecioMercadoPago()` + `formatearPesosUY()` |
| `Frontend/Barberia/src/components/Agenda/AgendaForm/AgendaForm.jsx` | Si MP está habilitado y el usuario marca “Pagar con Mercado Pago”, muestra total y aviso con `montoExtra` |
| `Frontend/Barberia/src/pages/Public/AgendaPage.jsx` | Pasa `precioNeto={servicioSeleccionado?.precio}` al formulario |

**Importante:** backend y frontend deben mantener **las mismas constantes**; si MP cambia tarifas, actualizar ambos archivos.

### Texto UI (gestión online)

> El total incluye un costo de gestión online de **$ {monto_extra}** para garantizar la reserva y procesar tu pago de forma segura.

Estilos: `AgendaForm.css` → clases `.af-mp-total*`.

### Flag de feature

`AgendaForm.jsx` → `MERCADO_PAGO_ENABLED` (boolean). En producción conviene `true` cuando las credenciales y URLs de MP estén listas.

---

## Flujo reserva con MP

1. Cliente elige servicio (precio neto en BD).
2. En el paso “Información”, opcionalmente marca pago con MP.
3. Frontend muestra `precio_final` y `monto_extra` (cálculo local).
4. `POST /visitas` con `medio_pago: "mercadopago"`.
5. Backend crea visita `PENDIENTE_CONFIRMACION_MP`, preferencia MP con `unit_price = precio_final`.
6. Cliente paga en Checkout Pro; webhook/confirma con monto = `precio_final` en UYU.

`precio_al_reservar` en la visita sigue guardando el **neto** (precio del servicio al reservar).

---

## Variables de entorno (Mercado Pago)

Ver `Backend/.env.example`. Resumen producción **KingBarber**:

```env
PUBLIC_FRONTEND_URL=https://kingbarber.webhop.net
BACKEND_PUBLIC_URL=https://kingbarber.webhop.net/api
CORS_ORIGINS=https://kingbarber.webhop.net
MERCADOPAGO_PUBLIC_KEY=...
MERCADOPAGO_ACCESS_TOKEN=...
MERCADOPAGO_WEBHOOK_SECRET=...
```

- **back_urls** (retorno tras pagar): `{PUBLIC_FRONTEND_URL}/agenda/pago-resultado?...`
- **notification_url** (webhook): `{BACKEND_PUBLIC_URL}/visitas/mercadopago/webhook`  
  En Apache, `/api` hace proxy a FastAPI → la URL pública lleva `/api`.

Desarrollo: usar `MERCADOPAGO_TUNNEL_URL` (ngrok al puerto 8000) y otro `PUBLIC_FRONTEND_URL` (IP local, localhost, etc.). No mezclar credenciales de prueba con producción en el mismo deploy.

---

## Credenciales de prueba vs producción

| Tipo | Uso |
|------|-----|
| **Prueba** | Panel MP → Credenciales de prueba; tarjetas TEST; opcional ngrok |
| **Producción** | Credenciales de producción en `.env` del servidor; dominio `kingbarber.webhop.net` |

Tokens `APP_USR-...` de producción no deben subirse a git (`.env` está en `.gitignore`).

---

## Checklist al activar o cambiar tarifas

- [ ] Actualizar `MP_COMISION_BASE` / `MP_IVA_SOBRE_COMISION` en Python y JS
- [ ] Probar `calcular_precio_mercadopago(350)` → 372,69 / 22,69
- [ ] Verificar preferencia MP con `unit_price` bruto
- [ ] Verificar webhook acepta `transaction_amount` esperado
- [ ] Revisar copy del aviso en AgendaForm

---

## Referencias en código

```python
# Backend
from utils.mercadopago_pricing import calcular_precio_mercadopago
p = calcular_precio_mercadopago(350)
# p.precio_final, p.monto_extra
```

```javascript
// Frontend
import { calcularPrecioMercadoPago } from "../../utils/mercadopagoPricing";
const { precioFinal, montoExtra } = calcularPrecioMercadoPago(350);
```
