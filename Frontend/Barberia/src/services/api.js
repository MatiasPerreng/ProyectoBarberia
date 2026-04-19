/** Base del API: VITE_API_URL o, en dev sin variable, proxy Vite `/api` → backend. */
const v = import.meta.env.VITE_API_URL;
const API_URL =
  v != null && String(v).trim() !== ""
    ? String(v).trim().replace(/\/+$/, "")
    : "/api";

export default API_URL;
