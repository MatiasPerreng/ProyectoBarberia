import API_URL from "./api";
import { formatFastApiDetail, networkFailureMessage } from "../utils/apiError";

export async function crearCliente(datos) {
  let response;
  try {
    response = await fetch(`${API_URL}/clientes/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(datos),
    });
  } catch (e) {
    throw new Error(networkFailureMessage(e));
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const msg = formatFastApiDetail(body) || "Error al crear cliente";
    console.error("Error backend /clientes:", body);
    throw new Error(msg);
  }

  return body;
}
