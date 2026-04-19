import API_URL from "./api";
import { networkFailureMessage } from "../utils/apiError";

/**
 * Cliente HTTP centralizado.
 * - Añade Authorization cuando hay token (excepto si requireAuth: false)
 * - Redirige a login en 401
 * - Fallos de red: lanza Error con mensaje claro
 */
export async function apiFetch(path, options = {}) {
  const { requireAuth = true, ...fetchOptions } = options;
  const token = localStorage.getItem("token");
  const isFormData = fetchOptions.body instanceof FormData;
  const headers = {
    ...(!isFormData && { "Content-Type": "application/json" }),
    ...(requireAuth && token && { Authorization: `Bearer ${token}` }),
    ...fetchOptions.headers,
  };
  const url = path.startsWith("http") ? path : `${API_URL}${path}`;
  let res;
  try {
    res = await fetch(url, { ...fetchOptions, headers });
  } catch (e) {
    throw new Error(networkFailureMessage(e));
  }
  if (res.status === 401 && requireAuth) {
    localStorage.removeItem("token");
    window.location.href = "/login-barbero";
  }
  return res;
}
