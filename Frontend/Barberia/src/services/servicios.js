import API_URL from "./api";

/* =========================
   GET
========================= */
export async function getServicios() {
  const res = await fetch(`${API_URL}/servicios/`);
  if (!res.ok) throw new Error("Error cargando servicios");
  return res.json();
}

/* =========================
   CREATE (JSON)
========================= */
export async function createServicio(data) {
  const res = await fetch(`${API_URL}/servicios/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      nombre: data.nombre,
      duracion_min: Number(data.duracion_min),
      precio: Number(data.precio),
      activo: true,
      imagen: data.imagen || null,
    }),
  });

  if (!res.ok) throw new Error("Error creando servicio");
  return res.json();
}

/* =========================
   UPDATE (JSON)
========================= */
export async function updateServicio(id, data) {
  const res = await fetch(`${API_URL}/servicios/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      nombre: data.nombre,
      duracion_min: Number(data.duracion_min),
      precio: Number(data.precio),
      activo: data.activo ?? true,
      imagen: data.imagen ?? null,
    }),
  });

  if (!res.ok) throw new Error("Error actualizando servicio");
  return res.json();
}

/* =========================
   DELETE
========================= */
export async function deleteServicio(id) {
  const res = await fetch(`${API_URL}/servicios/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) throw new Error("Error eliminando servicio");
  return true;
}
