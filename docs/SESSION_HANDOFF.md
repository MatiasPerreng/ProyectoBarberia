# Handoff — Barbería (contexto recuperado)

Resumen para continuar con el repo **sin depender del chat anterior**.

## Frontend (`Frontend/Barberia/`)

### Estilos globales admin
- **`src/styles/adminSurfaces.css`** (import en **`main.jsx`**): variables `--kb-app-bg-canvas` (`#faf9f7`), `--kb-admin-bg-surface` (`#ffffff`), sombras difusas (`--kb-shadow-admin-toolbar`, `--kb-shadow-admin-card`, hover, filtros, cards oscuras servicios).
- **`src/styles/layoutPageTitles.css`**: shell **`admin-kb-page`** con fondo **transparente** (el lienzo lo da `.admin-content`); overrides de **`kb-page-title`** para Perfil, Lista negra, Estadísticas donde aplica.
- **`AdminLayout.css`** / **`BarberoLayout.css`**: lienzo principal `var(--kb-app-bg-canvas)`.
- **`main.jsx`**: `layoutPageTitles.css`, `adminSurfaces.css`, `SuccessModal.css`, `modalsShared.css`.

### Sidebar admin (`AdminLayout.jsx`)
Orden priorizado: **Dashboard** → **Mi agenda** → **Historial** → **Barberos** → **Horarios** → **Servicios** → **Estadísticas** → **Carrusel** → **Lista Negra** → **Mi perfil** (cuenta al final).

### Historial de agenda (`pages/Shared/Historial/`)
- **`HistorialAgenda.jsx`**: texto en **`kb-narrativa-lead`** (fecha + `kb-narrativa-hora` con `a las HH:MM` + espacio fino + `hs`, `nowrap`), **`kb-narrativa-sep--comma`** (solo desktop), **`kb-narrativa-rest`** (cliente, `se\u00a0hizo`, servicio, barbero).
- **`HistorialAgenda.css`**: móvil ≤640px — lead en bloque con borde inferior; coma oculta entre bloques; padding vertical simétrico en cards; `hyphens: none`, `overflow-wrap` en servicio.

### Barberos (`pages/Admin/BarberoPage/`)
- Móvil: grilla **3 columnas** para Activar / Foto / Descanso (sin pirámide 2+1); **Eliminar** ancho completo; **768–960px** misma lógica en tablet.
- Cards: superficies blancas con variables; sombras admin.

### Servicios admin (`ServicioPage`, `ServicioCard`)
- Cards oscuras estilo listado público; botones columna; **Eliminar** rojo con texto oscuro; **`HorarioPage.css`**: **`.btn-delete`** acotado a **`.horarios-page-root`** para no pisar colores en otras vistas.

### Perfil (`pages/Shared/Perfil/`)
- **`admin-kb-page`** si ruta `/admin/*`; header tarjeta; card datos clara; botones primario/secundario legibles.

### Estadísticas (`pages/Shared/Estadisticas/`)
- Shell admin; KPI con **tabular-nums**; filtros en tarjeta; gráfico Recharts con ticks Inter + `fontFeatureSettings` en eje Y; tooltip estilizado.

### Lista negra (`pages/Admin/BlacklistPage/`)
- **`admin-kb-page`** + **`blist-page-root`**; cabecera toolbar; formulario y tabla con tokens admin; **Desbloquear** rojo + texto oscuro; móvil cards.

### Otras rutas tocadas
- **Blacklist**, **Estadísticas**, **AdminDashboard** (`TurnosList`, cards KPI), **HorarioList**, **HorarioPage**, **ServicioPage**, **Perfil**, **Historial**: fondos/sombras alineados a variables.
- **Modales**: `modalsShared.css`, ajustes en varios `*Modal.css` (ver conversación).

### Red / dev
- **`vite.config.js`**: `allowedHosts` para IPs LAN/pública (ej. `179.27.203.212`).
- **`Backend/main.py`**: CORS/orígenes — revisar en despliegue.

### Git
- **No commitear** `Frontend/Barberia/.env`, `Backend/venv/`, `**/__pycache__/**`, subidas locales en `Backend/static/` si no corresponden al repo.

## Backend (recordatorio anterior)

### `Backend/routers/estadisticas.py`
- `_primera_fecha_completada`, default de rango cuando `agrupacion=dia`, etc. (ver historial de commits).

Despliegue API: actualizar archivos + reiniciar servicio si aplica.

## Rutas útiles
- Admin: `/admin`, `/admin/mi-agenda`, `/admin/historial`, `/admin/barberos`, `/admin/horarios`, `/admin/servicios`, `/admin/estadisticas`, `/admin/carrusel`, `/admin/blacklist`, `/admin/perfil`
- Barbero: `/barbero`, `/barbero/historial`, `/barbero/estadisticas`, `/barbero/perfil`

## Pendiente / no incluido
- `.env` no versionado; variables en hosting.
- Revisar cambios locales en `Backend/` (pyc, `database.py`, `main.py`) antes de merge si no forman parte del mismo feature.

---
*Actualizado con el estado del UI admin (2026); mantener al día si el flujo cambia.*
