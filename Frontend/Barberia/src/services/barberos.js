import API_URL from "./api";

export async function getAgendaBarbero(barberoId) {
  const res = await fetch(
    `${API_URL}/barberos/${barberoId}/agenda`
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Error al cargar agenda del barbero");
  }

  return await res.json();
}


export async function getBarberos() {
  const res = await fetch(`${API_URL}/barberos/`);
  if (!res.ok) throw new Error("Error al cargar barberos");
  return await res.json();
}

export async function crearBarbero(data) {
  const res = await fetch(`${API_URL}/barberos/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al crear barbero");
  }

  return await res.json();
}

export async function toggleBarbero(idBarbero, activo) {
  const res = await fetch(
    `${API_URL}/barberos/${idBarbero}/estado`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ activo }),
    }
  );

  if (!res.ok) {
    throw new Error("Error al actualizar estado");
  }

  return await res.json();
}