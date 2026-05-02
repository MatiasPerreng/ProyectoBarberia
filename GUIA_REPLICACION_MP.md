# Guía: Mercado Pago Checkout Pro en King Barber (visitas)

Réplica del flujo típico de un **pedido** en e‑commerce, pero acá la unidad es **`visita`** (turno): se reserva el horario, se crea la preferencia de pago, el cliente paga en Mercado Pago, el webhook y/o la pantalla de retorno confirman el turno.

## 1. Base de datos

Ejecutá en MySQL/MariaDB (una vez):

```bash
mysql -u ... -p barber < Database/add_visita_mercadopago.sql
```

Eso agrega:

- Estado `PENDIENTE_CONFIRMACION_MP`
- Columnas `medio_pago`, `mp_preference_id`, `mp_payment_id`, `mp_status`, `token_seguimiento`

## 2. Variables de entorno (Backend)

En `Backend/.env` (no commitear credenciales):

| Variable | Uso |
|----------|-----|
| `MERCADOPAGO_ACCESS_TOKEN` | API privada (crear preferencia, leer pago) |
| `MERCADOPAGO_PUBLIC_KEY` | Se devuelve al front al crear turno con MP (Checkout Pro redirige con `init_point`) |
| `MERCADOPAGO_WEBHOOK_SECRET` | Opcional: validación de firma de notificaciones (no implementado en el MVP) |
| `PUBLIC_FRONTEND_URL` | **Obligatorio HTTPS** (MP bloquea `http://` en `back_urls` desde 2025). Ej.: `https://abc.ngrok-free.app` apuntando a tu Vite (`ngrok http 5174`). |
| `BACKEND_PUBLIC_URL` | **HTTPS** para `notification_url` (webhook). Si no es `https://`, la preferencia se crea **sin** webhook. Ej.: `ngrok http 8000`. |

Ejemplo de bloque (reemplazá con tus claves de prueba de [Mercado Pago Developers](https://www.mercadopago.com.ar/developers)):

```env
MERCADOPAGO_PUBLIC_KEY=APP_USR-...
MERCADOPAGO_ACCESS_TOKEN=APP_USR-...
MERCADOPAGO_WEBHOOK_SECRET=...
PUBLIC_FRONTEND_URL=https://FRONT-XXXX.ngrok-free.app
BACKEND_PUBLIC_URL=https://API-YYYY.ngrok-free.app
```

**Importante:** `localhost` o `http://` en esas dos URLs **ya no sirven** para crear la preferencia. Abrí dos túneles (o el plan de ngrok que permita varios) y usá las URLs `https` que te da ngrok.

## 3. Puerto del front (Vite) y HTTPS local

El front usa el puerto **`5174`** y **`@vitejs/plugin-basic-ssl`**: al correr `npm run dev` la URL es **`https://localhost:5174`** (el navegador marcará el certificado como no confiable: es normal en desarrollo → avanzar / continuar).

En `Backend/.env`:

```env
PUBLIC_FRONTEND_URL=https://localhost:5174
```

Así Mercado Pago acepta las `back_urls` sin ngrok. Para el **webhook** seguís necesitando una URL pública HTTPS (p. ej. ngrok al `8000`) en `BACKEND_PUBLIC_URL`, o confirmás el pago solo con la pantalla de retorno + sincronizar.

## 4. ngrok (webhook en desarrollo)

1. Instalá [ngrok](https://ngrok.com/download) o `winget install ngrok.ngrok`.
2. Levantá el backend en `8000` y en otra terminal: `ngrok http 8000`.
3. Copiá la URL `https://....ngrok-free.app` (sin barra final) en `BACKEND_PUBLIC_URL`.
4. En el panel de MP, si hace falta, declará la misma URL de notificación (Checkout Pro ya envía `notification_url` en la preferencia).

Sin `BACKEND_PUBLIC_URL` pública, el **pago** puede completarse pero el **webhook** no llegará desde internet; igual podés confirmar con la ruta de **sincronización** al volver del checkout (ver abajo).

## 5. Flujo de API (resumen)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/visitas/` | Body JSON incluye `medio_pago`: `"efectivo"` (default) o `"mercadopago"`. Con MP: estado `PENDIENTE_CONFIRMACION_MP`, respuesta incluye `init_point` y `public_key`. |
| `GET` | `/visitas/seguimiento/sincronizar?token=...&payment_id=...` | Público. Lee el pago en MP, actualiza la visita y dispara email si pasó a `CONFIRMADO`. |
| `GET` | `/visitas/seguimiento/{token}` | Estado actual de la reserva (sin `payment_id`). |
| `POST` | `/visitas/mercadopago/webhook` | IPN de MP (`payment`). |

`external_reference` de la preferencia es el **`id_visita`**.

## 6. Front

- Ruta **`/agenda/pago-resultado`**: lee `token` y `payment_id` (o `collection_id`) de la query de retorno de MP y llama a sincronizar.
- La agenda pública permite elegir **Efectivo** o **Mercado Pago** antes de confirmar.

## 7. Comportamiento de negocio

- Turnos **pendientes de pago** ocupan el mismo hueco que un turno confirmado (no se puede doble reservar).
- Límite de **2 turnos por cliente y día** cuenta también los pendientes MP.
- La TV y la agenda del barbero siguen mostrando solo turnos **`CONFIRMADO`**.
- Email de confirmación: al pagar (webhook o sync), si pasa de pendiente a confirmado.

## 8. Prueba manual

1. Migración SQL aplicada y `.env` configurado.
2. `BACKEND_PUBLIC_URL` con ngrok si querés webhook real.
3. Front: `npm run dev` en `Frontend/Barberia` → `http://localhost:5174`.
4. Reservar con MP → redirección a MP → pagar con tarjeta de prueba → volver al sitio → mensaje en `/agenda/pago-resultado`.

Tarjetas de prueba: documentación oficial de Mercado Pago según país.
