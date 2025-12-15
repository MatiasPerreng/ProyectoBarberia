export async function crearVisita(data) {
  const res = await fetch('http://localhost:8000/visitas/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Error al crear visita');
  }

  return await res.json();
}


export async function getAgendaBarbero(idBarbero) {
  const res = await fetch(
    `http://localhost:8000/barberos/${idBarbero}/agenda`
  );

  if (!res.ok) {
    throw new Error("Error al cargar agenda");
  }

  return await res.json();
}
