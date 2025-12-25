import { useEffect, useState } from "react";
import AdminLayout from "../../components/Admin/AdminLayout/AdminLayout";
import BarberoForm from "../../components/Admin/BarberoForm/BarberoForm";
import "./BarberosPage.css";

import {
  getBarberos,
  crearBarbero,
  toggleBarbero,
} from "../../services/barberos";

const BarberosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);

  // ----------------------------
  // Cargar barberos
  // ----------------------------
  const loadBarberos = async () => {
    try {
      const data = await getBarberos();
      setBarberos(data);
    } catch (err) {
      console.error("Error cargando barberos:", err);
      setError("No se pudieron cargar los barberos");
    }
  };

  useEffect(() => {
    loadBarberos();
  }, []);

  // ----------------------------
  // Crear barbero (DEVUELVE EL BARBERO)
  // ----------------------------
  const handleCreate = async (data) => {
    try {
      const barbero = await crearBarbero(data);

      console.log("🧔‍♂️ Barbero creado:", barbero);

      await loadBarberos();
      setShowForm(false);

      // 🔑 CLAVE: devolver el barbero para que BarberoForm suba la foto
      return barbero;
    } catch (err) {
      console.error("Error creando barbero:", err);
      setError("No se pudo crear el barbero");
      throw err;
    }
  };

  // ----------------------------
  // Activar / Desactivar barbero
  // ----------------------------
  const handleToggle = async (barbero) => {
    try {
      await toggleBarbero(barbero.id_barbero, !barbero.activo);
      loadBarberos();
    } catch (err) {
      console.error("Error actualizando barbero:", err);
      setError("No se pudo actualizar el barbero");
    }
  };

  return (
    <AdminLayout>
      <div className="admin-page-header">
        <h2>Barberos</h2>

        <button onClick={() => setShowForm(true)}>
          + Nuevo barbero
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="admin-table">
        {barberos.map((b) => (
          <div className="admin-row" key={b.id_barbero}>
            <div>
              <strong>{b.nombre}</strong>
              {b.email && <small>{b.email}</small>}
            </div>

            <div className="admin-actions">
              <span
                className={`status ${
                  b.activo ? "active" : "inactive"
                }`}
              >
                {b.activo ? "Activo" : "Inactivo"}
              </span>

              <button onClick={() => handleToggle(b)}>
                {b.activo ? "Desactivar" : "Activar"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {showForm && (
        <BarberoForm
          onSubmit={handleCreate}
          onClose={() => setShowForm(false)}
        />
      )}
    </AdminLayout>
  );
};

export default BarberosPage;
