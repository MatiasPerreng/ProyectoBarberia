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
