import API_URL from "./api";

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

export async function subirFotoBarbero(idBarbero, file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `${API_URL}/barberos/${idBarbero}/foto`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al subir foto");
  }

  return await res.json();
}

export async function toggleBarbero(idBarbero, activo) {
  const res = await fetch(`${API_URL}/barberos/${idBarbero}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ activo }),
  });

  if (!res.ok) throw new Error("Error al actualizar barbero");
  return await res.json();
}


// ---------------------------
// AGENDA DEL BARBERO
// ---------------------------

export async function getAgendaBarbero() {
  const res = await fetch(`${API_URL}/barberos/mi-agenda`);

  if (!res.ok) {
    throw new Error("Error al cargar agenda del barbero");
  }

  return await res.json();
}
