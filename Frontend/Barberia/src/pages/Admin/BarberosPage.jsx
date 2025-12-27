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
  // Crear barbero
  // ----------------------------
  const handleCreate = async (data) => {
    try {
      const barbero = await crearBarbero(data);
      await loadBarberos();
      setShowForm(false);
      return barbero; // 👈 para subir foto
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
      // 🔥 optimista (opcional pero pro)
      setBarberos((prev) =>
        prev.map((b) =>
          b.id_barbero === barbero.id_barbero
            ? { ...b, activo: !b.activo }
            : b
        )
      );

      await toggleBarbero(barbero.id_barbero);
    } catch (err) {
      console.error("Error actualizando barbero:", err);
      setError("No se pudo actualizar el barbero");
      loadBarberos(); // rollback si falla
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
