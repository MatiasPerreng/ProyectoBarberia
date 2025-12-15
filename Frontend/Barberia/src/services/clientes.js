export async function crearCliente(datosCliente) {
  const res = await fetch('http://localhost:8000/clientes/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nombre: datosCliente.nombre,
      email: datosCliente.email,
      telefono: datosCliente.telefono || null
    })
  });

  if (!res.ok) {
    throw new Error('Error al crear cliente');
  }

  return await res.json();
}
