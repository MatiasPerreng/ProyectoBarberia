import { useEffect, useState } from "react";
import AdminLayout from "../../components/Admin/AdminLayout/AdminLayout";
import BarberoForm from "../../components/Admin/BarberoForm";
import './BarberoPage.css'

import {
  getBarberos,
  crearBarbero,
  toggleBarbero,
} from "../../services/barberos";

const BarberosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const loadBarberos = async () => {
    const data = await getBarberos();
    setBarberos(data);
  };

  useEffect(() => {
    loadBarberos();
  }, []);

  const handleCreate = async (data) => {
    await crearBarbero(data);
    setShowForm(false);
    loadBarberos();
  };

  const handleToggle = async (barbero) => {
    await toggleBarbero(barbero.id_barbero, !barbero.activo);
    loadBarberos();
  };

  return (
    <AdminLayout>
      <div className="admin-page-header">
        <h2>Barberos</h2>
        <button onClick={() => setShowForm(true)}>
          + Nuevo barbero
        </button>
      </div>

      <div className="admin-table">
        {barberos.map((b) => (
          <div className="admin-row" key={b.id_barbero}>
            <div>
              <strong>{b.nombre}</strong>
              <small>{b.email}</small>
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
