# Guía de implementación Mercado Pago — ProyectoBarberia (King Barber)

Documentación alineada con el **código actual** (FastAPI + React/Vite). No hay servicios separados tipo `checkout_service.py` ni `webhooks.py`: el flujo vive en **`Backend/utils/mercadopago_api.py`**, **`Backend/crud/visita.py`** y **`Backend/routers/visitas.py`**.

---

## 1. Visión general

- **Producto de MP:** Checkout Pro (preferencia + `init_point`).
- **Unidad de negocio:** la tabla **`visita`** (turno), no un carrito aparte.
- **Identificadores clave:**
  - `external_reference` en la preferencia = **`id_visita`** (string).
  - `metadata.token_seguimiento` = token opaco para URLs públicas sin JWT.
  - Tras pagar, MP redirige al front con query (`token`, `payment_id` / `collection_id`, `status`, etc.).
- **Confirmación del pago:** puede llegar por **webhook** (`/visitas/mercadopago/webhook`) y/o por **GET** de sincronización al volver del checkout (`/visitas/seguimiento/sincronizar`). Ambos llaman a la misma lógica de aplicar pago en BD.

---

## 2. Instalación y base de datos

### 2.1 Migración MP sobre `visita`

Ejecutar en MySQL/MariaDB (una vez):

```bash
mysql -u USUARIO -p NOMBRE_BD < Database/add_visita_mercadopago.sql
```

Efectos (`Database/add_visita_mercadopago.sql`):

- Extiende el `ENUM` de **`estado`** con **`PENDIENTE_CONFIRMACION_MP`**.
- Añade columnas: **`medio_pago`**, **`mp_preference_id`**, **`mp_payment_id`**, **`mp_status`**, **`token_seguimiento`**.
- Índice único **`ux_visita_token_seguimiento`** sobre `token_seguimiento`.

### 2.2 Índice único por slot activo (evitar doble turno)

Script idempotente:

```bash
mysql -u USUARIO -p NOMBRE_BD < Database/visita_slot_unique_activo.sql
```

Efectos (`Database/visita_slot_unique_activo.sql`):

- Opcionalmente elimina el índice antiguo **`uk_barbero_fecha`** si existía.
- Crea columna generada **`uq_slot_activo`** (NULL si `estado = CANCELADO`) y **`CREATE UNIQUE INDEX ux_visita_slot_activo`**.

Esto refuerza en BD lo que ya valida el CRUD: no dos turnos activos mismo barbero + `fecha_hora`.

### 2.3 Dependencias Python

En el backend ya se usa **`requests`** para llamadas REST a `https://api.mercadopago.com` (`mercadopago_api.py`). No hay SDK oficial obligatorio en este proyecto.

---

## 3. Configuración (.env)

### 3.1 Backend (`Backend/.env`)

Referencia comentada en **`Backend/.env.example`**. Variables relevantes MP:

| Variable | Rol en el código |
|----------|------------------|
| **`MERCADOPAGO_ACCESS_TOKEN`** | Obligatorio para crear preferencia y leer `payments` / `merchant_orders` (`_token()` en `mercadopago_api.py`). |
| **`MERCADOPAGO_PUBLIC_KEY`** | Se envía al front en `POST /visitas/` cuando hay `init_point` (`visitas.py`). |
| **`PUBLIC_FRONTEND_URL`** | Base **HTTPS** de las `back_urls`. Si no empieza por `https://`, **`create_checkout_preference` lanza error** (MP rechaza HTTP en retornos). |
| **`BACKEND_PUBLIC_URL`** | Si es **HTTPS**, se setea `notification_url` en la preferencia apuntando a **`{BACKEND_PUBLIC_URL}/visitas/mercadopago/webhook`**. Si no es HTTPS, **no se envía webhook** (solo sync al volver + posibles IPN si configurás manual). |
| **`MERCADOPAGO_PREFERENCE_EXPIRATION_MINUTES`** | Opcional (default **10**). Alineado con la cancelación automática de pendientes en BD (`preference_expiration_minutes()`). |
| **`MERCADOPAGO_COMPROBANTE_URL`** | Plantilla del recibo público; `{payment_id}` se reemplaza en `comprobante_url_public()` (default `.uy`). |

**Gap documentado:** en `.env.example` aparece **`MERCADOPAGO_WEBHOOK_SECRET`**; en el código **no hay verificación de firma/x-signature** del webhook. Es solo reserva para un futuro hardening.

### 3.2 HTTPS local (front)

`mercadopago_api.py` documenta: Vite con **`@vitejs/plugin-basic-ssl`** en puerto **5174** → `PUBLIC_FRONTEND_URL=https://localhost:5174`.

### 3.3 Frontend (`Frontend/Barberia/.env`)

Variables opcionales para pantalla de resultado / soporte (ver `VisitaPagoResultado.jsx`):

- `VITE_WHATSAPP_TURNO`, `VITE_WHATSAPP_TURNO_LABEL`
- `VITE_MP_REEMBOLSO_URL`

---

## 4. Creación de preferencia (Checkout Pro)

**Archivo:** `Backend/utils/mercadopago_api.py` → `create_checkout_preference(...)`.

Comportamiento real:

1. **`items`:** un ítem, `currency_id: "UYU"`, `unit_price` redondeado (si es 0, se fuerza **1.0** para no romper MP).
2. **`external_reference`:** `str(id_visita)`.
3. **`metadata`:** `{"token_seguimiento": "<token>"}` (redundante con query en `back_urls`, útil para trazabilidad).
4. **`back_urls`:** `{PUBLIC_FRONTEND_URL}/agenda/pago-resultado` con query **`token`** + **`mp_return`** (`ok` | `fail` | `pending`) — función interna `_return_url`.
5. **`auto_return`:** `"approved"`.
6. **Vigencia:** `expires`, `expiration_date_from` / `expiration_date_to` en zona **`America/Montevideo`** (`_preference_expiration_fields`).
7. **`notification_url`:** solo si `BACKEND_PUBLIC_URL` es HTTPS.
8. **`payer.email`:** opcional, si el cliente tiene email en BD al crear la visita.

Respuesta normalizada: **`{"id", "init_point", "raw"}`** (`id` = `preference_id`).

**Archivo:** `Backend/crud/visita.py` → `create_visita`:

- Si `medio_pago == "mercadopago"`: estado **`PENDIENTE_CONFIRMACION_MP`**, `medio_pago` columna **`MERCADOPAGO`**, genera `token_seguimiento`, tras `flush` crea preferencia y guarda **`mp_preference_id`**, devuelve **`init_point`** al router.

---

## 5. Rutas HTTP (FastAPI)

Prefijo del router: **`/visitas`** (`visitas.py`).

| Método | Ruta | Uso |
|--------|------|-----|
| `POST` | `/visitas/` | Crea visita; con MP devuelve `init_point` + `public_key` en el JSON (`visita_to_out` + campos extra). |
| `GET` | `/visitas/seguimiento/{token}` | Estado de la visita por token (público). |
| `GET` | `/visitas/seguimiento/sincronizar?token=&payment_id=` | Tras volver de MP: lee pago con `get_payment`, aplica **`aplicar_pago_mercadopago`**, opcional email en background. |
| **`GET` y `POST`** | **`/visitas/mercadopago/webhook`** | **Un solo endpoint** (`@router.api_route`). Acepta JSON (POST) y query tipo IPN (GET). |

**Variación respecto a guías genéricas:** el webhook **no** está en un archivo aparte ni solo POST; el parseo unificado está en **`_parse_mp_notification_ids`**.

---

## 6. Webhook e IPN

**Archivo:** `Backend/routers/visitas.py`.

### 6.1 Entrada

- **POST:** intenta `await request.json()`; si falla, body `{}`.
- **`_parse_mp_notification_ids`:** obtiene **`payment_id`** y/o **`merchant_order_id`** desde:
  - Query `topic`/`type` + `id` (p. ej. IPN clásico).
  - Cuerpo JSON `type`/`topic`, `data.id`, `resource` (URL con `/payments/` o `/merchant_orders/`).
  - Fallback `data.id` / `id` en query.

Si no hay ningún id → **`{"ok": true, "ignored": true}`** (200, sin trabajo).

### 6.2 Procesamiento (orden real)

1. **`cancelar_visitas_mp_expiradas(db)`** — libera pendientes viejos antes de aplicar pagos (evita estados incoherentes).
2. Si hay **`merchant_order_id`:** `get_merchant_order` → **`procesar_merchant_order_mp`** (cancela visita pendiente si la orden indica **expired / cancelado / closed sin pago**, matcheando por **`mp_preference_id`**).
3. Si hay **`payment_id`:** `get_payment` → `external_reference` debe ser **`id_visita`** → **`aplicar_pago_mercadopago`** → email en background si corresponde.

Todo el bloque está envuelto en **`try/except`** con log; **siempre** termina en **`return {"ok": True}`** para que MP no reintente por error 5xx en fallos internos puntuales.

**Gaps / estabilidad:**

- **200 siempre al final:** prioridad “no pelear con MP”; errores → logs + investigación.
- **Sin validación de firma:** cualquiera que conozca la URL podría POSTear; mitigación típica sería secret en header o firma MP + `MERCADOPAGO_WEBHOOK_SECRET` (pendiente).
- **Idempotencia de negocio:** `aplicar_pago_mercadopago` actualiza según `status`; el email solo si **`aplicar_pago_mercadopago` devuelve `True`** (transición a `CONFIRMADO` desde `PENDIENTE_CONFIRMACION_MP` o reactivación desde `CANCELADO` — ver crud).

---

## 7. Sincronización con la BD y estados

**Archivo:** `Backend/crud/visita.py`.

### 7.1 `aplicar_pago_mercadopago(db, visita, payment_data)`

- Valida **`external_reference`** == `id_visita` (si no, **`ValueError`**).
- **`approved` / `authorized`:**  
  - Pendiente → **`CONFIRMADO`**.  
  - **`CANCELADO`** (p. ej. timeout local) + medio MP → **reactiva a `CONFIRMADO`** solo si **`_otro_turno_activo_solapa`** es falso; si el hueco fue tomado, deja cancelado y loguea warning.
- Estados finales negativos (`rejected`, `cancelled`, `refunded`, … o `expired` en `status_detail`): si estaba pendiente → **`CANCELADO`**.
- Guarda **`mp_payment_id`**, **`mp_status`**.
- Retorno **`True`** si conviene enviar email: quedó **`CONFIRMADO`** y el estado previo era **`PENDIENTE_CONFIRMACION_MP`** o **`CANCELADO`**.

### 7.2 `cancelar_visitas_mp_expiradas`

- SQL crudo con **`DATE_SUB(NOW(), INTERVAL N MINUTE)`** y `N` interpolado como entero acotado (evita problemas de bind en `INTERVAL` con algunos drivers).
- **`db.commit()`** explícito + **`expire_all()`** (evita rollback silencioso al cerrar sesión sin commit).

### 7.3 `procesar_merchant_order_mp`

- Usa **`_merchant_order_implica_fin_sin_pago`** (inspecciona `order_status`, `status`, lista `payments`, `paid_amount`).
- Busca visita **`PENDIENTE_CONFIRMACION_MP`** con **`mp_preference_id`** = `preference_id` de la orden.

### 7.4 Reglas ligadas al flujo MP

- **`cliente_tiene_limite_turnos`:** cuenta **`CONFIRMADO`** + **`PENDIENTE_CONFIRMACION_MP`** (máx. 2 / día).
- **`get_disponibilidad`** / **`create_visita`:** excluyen solo **`CANCELADO`** del solape; pendientes MP **ocupan** el slot.
- **Agenda barbero / TV:** listados de “agenda del día” usan **`CONFIRMADO`** (pendiente MP no molesta en pantalla hasta confirmar).

---

## 8. Frontend (resultado de pago)

- **Ruta:** `/agenda/pago-resultado` (`AppRouter.jsx`).
- **Servicio:** `Frontend/Barberia/src/services/agenda.js`:
  - Con `payment_id` o `collection_id` → **`GET .../visitas/seguimiento/sincronizar`**.
  - Sin id de cobro → solo **`GET .../visitas/seguimiento/{token}`** (estado informativo).
- **UI:** `VisitaPagoResultado.jsx` — estados `ok`, `fallo` (sync devuelve cancelado, p. ej. slot tomado), `pendiente`, `info`, `error`.
- **Comprobante MP:** URL desde backend en **`comprobante_mp_url`** (`comprobante_url_public` + `MERCADOPAGO_COMPROBANTE_URL`). Estilos compartidos: **`Frontend/Barberia/src/styles/mpComprobanteBtn.css`** (`.kb-mp-comprobante`).

---

## 9. Panel admin y agenda barbero

- **`Backend/routers/admin.py`:** en listados de turnos, arma **`comprobante_mp_url`** con el mismo helper si hay `mp_payment_id` y medio MP.
- **`BarberoAgendaItem`:** mismo link visual (clases `kb-mp-comprobante`).

---

## 10. Correo transaccional (gap operativo)

**Archivo:** `Backend/core/email.py`.

- Config **lazy** (`MAIL_ENABLED`, credenciales completas); si falta algo, no rompe el import.
- **`ConnectionErrors`** (SMTP, p. ej. Gmail **534 WebLoginRequired**) se **loguean** y **no se relanzan** en tareas en background, para no tumbar la respuesta HTTP del pago.
- Gmail: contraseña de **aplicación**, no la de la cuenta (documentado en `.env.example`).

---

## 11. CORS

**Archivo:** `Backend/main.py` — `CORSMiddleware` incluye orígenes `localhost`/`127.0.0.1` **5173 y 5174** (http y https). Si el front público queda en otro host (ngrok), hay que **añadir ese origen** a `allow_origins` o el browser bloqueará la llamada a `sincronizar`.

---

## 12. Checklist de prueba manual

1. Migraciones **`add_visita_mercadopago.sql`** y, si aplica, **`visita_slot_unique_activo.sql`**.
2. `.env` con token y keys MP + **`PUBLIC_FRONTEND_URL`** HTTPS.
3. Opcional: **`BACKEND_PUBLIC_URL`** HTTPS (ngrok al puerto del API) para webhook real.
4. Reservar con **`medio_pago`: `"mercadopago"`** desde la agenda pública.
5. Pagar en sandbox MP → volver al sitio → verificar **`CONFIRMADO`**, email (si SMTP OK), comprobante en admin/mi-agenda.

---

## 13. Nota final: webhook, 200 OK y duplicados

**Prestá especial atención a cómo quedó configurado el endpoint del webhook** (`/visitas/mercadopago/webhook`, GET y POST):

- Responde **200** con **`{"ok": true}`** incluso tras errores internos logueados, para reducir reintentos agresivos de MP por 5xx.
- **No hay verificación criptográfica de notificaciones** en esta versión; la coherencia depende de **`get_payment`** / **`get_merchant_order`** con token de servidor y de **`external_reference`**.
- Los **duplicados de notificación** MP suelen ser idempotentes a nivel negocio: re-aplicar **`approved`** sobre una visita ya **`CONFIRMADO`** no dispara otro email salvo la condición explícita del `return` en **`aplicar_pago_mercadopago`** (transición desde pendiente o cancelado-reactivación).

Para endurecer en producción: validar firma de webhook (documentación MP), usar **`MERCADOPAGO_WEBHOOK_SECRET`**, y/o registrar **`payment_id`** ya procesados.

---

*Última revisión alineada con el repositorio **ProyectoBarberia** (FastAPI + React). Archivos tocados frecuentemente: `mercadopago_api.py`, `crud/visita.py`, `routers/visitas.py`, `models/visita.py`, `VisitaPagoResultado.jsx`, `agenda.js`.*
