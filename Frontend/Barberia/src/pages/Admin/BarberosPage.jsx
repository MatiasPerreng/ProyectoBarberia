import { useEffect, useRef, useState } from "react";
import AdminLayout from "../../components/Admin/AdminLayout/AdminLayout";
import BarberoForm from "../../components/Admin/BarberoForm/BarberoForm";
import Footer from "../../components/Footer/Footer";
import "./BarberosPage.css";

import {
  getBarberos,
  crearBarbero,
  toggleBarbero,
  subirFotoBarbero,
  eliminarBarbero,
} from "../../services/barberos";

import API_URL from "../../services/api";

const BarberosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const [barberoFotoTarget, setBarberoFotoTarget] = useState(null);

  // ----------------------------
  // Cargar barberos
  // ----------------------------
  const loadBarberos = async () => {
    try {
      const data = await getBarberos();
      setBarberos(data);
    } catch (err) {
      console.error(err);
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
    const barbero = await crearBarbero(data);
    await loadBarberos();
    setShowForm(false);
    return barbero;
  };

  // ----------------------------
  // Toggle activo
  // ----------------------------
  const handleToggle = async (barbero) => {
    setBarberos((prev) =>
      prev.map((b) =>
        b.id_barbero === barbero.id_barbero
          ? { ...b, activo: !b.activo }
          : b
      )
    );

    try {
      await toggleBarbero(barbero.id_barbero);
    } catch {
      loadBarberos();
    }
  };

  // ----------------------------
  // Eliminar barbero
  // ----------------------------
  const handleDelete = async (barbero) => {
    if (
      !confirm(
        `¿Eliminar definitivamente al barbero "${barbero.nombre}"?`
      )
    )
      return;

    try {
      await eliminarBarbero(barbero.id_barbero);
      loadBarberos();
    } catch (err) {
      alert(err.message);
    }
  };

  // ----------------------------
  // Cambiar foto
  // ----------------------------
  const handleSelectFoto = (barbero) => {
    setBarberoFotoTarget(barbero);
    fileInputRef.current.click();
  };

  const handleUploadFoto = async (e) => {
    const file = e.target.files[0];
    if (!file || !barberoFotoTarget) return;

    try {
      await subirFotoBarbero(barberoFotoTarget.id_barbero, file);
      loadBarberos();
    } catch (err) {
      alert("Error al subir foto");
    } finally {
      e.target.value = "";
      setBarberoFotoTarget(null);
    }
  };

  return (
    <>
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
              {/* FOTO */}
              <img
                className="admin-avatar"
                src={
                  b.foto_url
                    ? `${API_URL}${b.foto_url}`
                    : "/barbero-placeholder.png"
                }
                alt={b.nombre}
              />

              {/* INFO */}
              <div className="admin-info">
                <strong>{b.nombre}</strong>
              </div>

              {/* ACCIONES */}
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

                <button onClick={() => handleSelectFoto(b)}>
                  Cambiar foto
                </button>

                <button
                  className="danger"
                  onClick={() => handleDelete(b)}
                >
                  Eliminar
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

        {/* INPUT FILE OCULTO */}
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleUploadFoto}
        />
      </AdminLayout>

      <Footer />
    </>
  );
};

export default BarberosPage;
