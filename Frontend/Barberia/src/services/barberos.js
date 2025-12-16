export async function getAgendaBarbero(barberoId) {
  const res = await fetch(
    `http://localhost:8000/barberos/${barberoId}/agenda`
  );

  if (!res.ok) {
    throw new Error("Error al cargar agenda del barbero");
  }

  return await res.json();
}
