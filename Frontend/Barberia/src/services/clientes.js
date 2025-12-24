const API_URL = "http://127.0.0.1:8000";

export async function crearCliente(datos) {
  const response = await fetch(`${API_URL}/clientes/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(datos),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error("Error backend /clientes:", error);
    throw new Error(error.detail || "Error al crear cliente");
  }

  return await response.json();
}
