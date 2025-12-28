import API_URL from "./api";

// =======================================================
// BARBEROS
// =======================================================

export async function getBarberos() {
  const res = await fetch(`${API_URL}/barberos/`);

  if (!res.ok) {
    throw new Error("Error al cargar barberos");
  }

  return await res.json();
}

export async function crearBarbero(data) {
  const res = await fetch(`${API_URL}/barberos/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
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

  const res = await fetch(`${API_URL}/barberos/${idBarbero}/foto`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al subir foto");
  }

  return await res.json();
}

export async function toggleBarbero(idBarbero) {
  const res = await fetch(`${API_URL}/barberos/${idBarbero}/toggle`, {
    method: "PATCH",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al cambiar estado del barbero");
  }

  return await res.json();
}

export async function eliminarBarbero(idBarbero) {
  const res = await fetch(`${API_URL}/barberos/${idBarbero}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al eliminar barbero");
  }

  // no siempre devuelve body, por las dudas:
  return res.status === 204 ? true : await res.json();
}

// =======================================================
// AGENDA DEL BARBERO (CON AUTH)
// =======================================================

export async function getAgendaBarbero() {
  const res = await fetch(`${API_URL}/barberos/mi-agenda`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Error al cargar agenda del barbero");
  }

  return await res.json();
}

// =======================================================
// CREAR CUENTA (LOGIN) PARA BARBERO — ADMIN
// =======================================================

/**
 * @param {number} barberoId  -> ID del barbero (VA EN LA URL)
 * @param {object} data       -> { nombre, email, password, rol }
 */
export async function crearCuentaBarbero(barberoId, data) {
  if (!barberoId) {
    throw new Error("ID de barbero inválido");
  }

  const res = await fetch(
    `${API_URL}/barberos/${barberoId}/crear-acceso`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify(data),
    }
  );

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al crear la cuenta del barbero");
  }

  return await res.json();
}
