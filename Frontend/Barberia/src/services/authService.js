const API_URL = "http://127.0.0.1:8000";

export async function loginBarbero(email, password) {
  const response = await fetch(`${API_URL}/auth/login-barbero`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error al iniciar sesión");
  }

  return await response.json();
}
