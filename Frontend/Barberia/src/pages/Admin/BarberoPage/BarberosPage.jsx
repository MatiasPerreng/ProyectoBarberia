import { useEffect, useRef, useState } from "react";
import BarberoForm from "../../../components/Admin/BarberoForm/BarberoForm";
import "./BarberosPage.css";

import {
  getBarberos,
  crearBarbero,
  toggleBarbero,
  subirFotoBarbero,
  eliminarBarbero,
} from "../../../services/barberos";

import API_URL from "../../../services/api";

const BarberosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const [alertError, setAlertError] = useState(null);

  /* =========================
      FOTO (REFS Y ESTADOS)
  ========================= */
  const fileInputRef = useRef(null);
  const [fileInputKey, setFileInputKey] = useState(0);
  const [barberoFotoTargetId, setBarberoFotoTargetId] = useState(null);

  /* =========================
      LOAD BARBEROS
  ========================= */
  const loadBarberos = async () => {
    try {
      const data = await getBarberos();

      setBarberos((prev) =>
        data.map((b) => {
          const prevB = prev.find((p) => p.id_barbero === b.id_barbero);
          return {
            ...b,
            // Preservamos el timestamp para evitar que la imagen "parpadee" a la vieja
            _fotoUpdatedAt: prevB?._fotoUpdatedAt || 0,
          };
        })
      );
    } catch (err) {
      setError("No se pudieron cargar los barberos");
    }
  };

  useEffect(() => {
    loadBarberos();
  }, []);

  /* =========================
      ACCIONES (CREAR, TOGGLE, DELETE)
  ========================= */
  const handleCreate = async (data) => {
    try {
      // 🔥 IMPORTANTE: Retornamos el resultado de la API
      // Esto permite que BarberoForm reciba el id_barbero
      const nuevoBarbero = await crearBarbero(data);
      return nuevoBarbero; 
    } catch (err) {
      setAlertError("Error al crear el barbero en el servidor");
      throw err; // Propaga el error al formulario
    }
  };

  const handleToggle = async (barbero) => {
    setBarberos((prev) =>
      prev.map((b) =>
        b.id_barbero === barbero.id_barbero ? { ...b, activo: !b.activo } : b
      )
    );
    try {
      await toggleBarbero(barbero.id_barbero);
    } catch {
      loadBarberos();
    }
  };

  const handleDelete = async (barbero) => {
    try {
      await eliminarBarbero(barbero.id_barbero);
      loadBarberos();
    } catch (err) {
      setAlertError(
        err?.message || "No se puede eliminar el barbero tiene datos asociados."
      );
    }
  };

  /* =========================
      CAMBIO DE FOTO (EDICIÓN)
  ========================= */
  const handleSelectFoto = (barbero) => {
    setBarberoFotoTargetId(barbero.id_barbero);
    setFileInputKey((k) => k + 1);
    setTimeout(() => {
      fileInputRef.current?.click();
    }, 10);
  };

  const handleUploadFoto = async (e) => {
    const file = e.target.files[0];
    if (!file || !barberoFotoTargetId) return;

    try {
      const res = await subirFotoBarbero(barberoFotoTargetId, file);
      
      const newTimestamp = Date.now();
      setBarberos((prev) =>
        prev.map((b) =>
          b.id_barbero === barberoFotoTargetId
            ? { 
                ...b, 
                foto_url: res?.foto_url || b.foto_url, 
                _fotoUpdatedAt: newTimestamp 
              }
            : b
        )
      );
    } catch (err) {
      setAlertError("No se pudo actualizar la imagen.");
    } finally {
      setBarberoFotoTargetId(null);
    }
  };

  return (
    <div className="barberos-page-container">
      <div className="barberos-header">
        <h2>Barberos</h2>
        <button className="barberos-btn-primary" onClick={() => setShowForm(true)}>
          + Nuevo barbero
        </button>
      </div>

      {error && <p className="barberos-error">{error}</p>}

      <div className="barberos-list">
        {barberos.map((b) => (
          <div className="barberos-row" key={b.id_barbero}>
            <img
              className="barberos-avatar"
              src={
                b.foto_url
                  ? `${API_URL}${b.foto_url}?v=${b._fotoUpdatedAt || 0}`
                  : "/avatar-placeholder.png"
              }
              alt={b.nombre}
            />

            <div className="barberos-info">
              <strong>{b.nombre}</strong>
            </div>

            <span className={`barberos-status ${b.activo ? "active" : "inactive"}`}>
              {b.activo ? "Activo" : "Inactivo"}
            </span>

            <div className="barberos-actions">
              <button onClick={() => handleToggle(b)}>
                {b.activo ? "Desactivar" : "Activar"}
              </button>
              <button onClick={() => handleSelectFoto(b)}>Cambiar foto</button>
              <button className="danger" onClick={() => handleDelete(b)}>Eliminar</button>
            </div>
          </div>
        ))}
      </div>

      {showForm && (
        <BarberoForm
          onSubmit={handleCreate}
          onClose={() => setShowForm(false)}
          onCreated={() => {
            setShowForm(false);
            loadBarberos(); 
          }}
        />
      )}

      {alertError && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h3>Atención</h3>
            <p style={{ textAlign: "center" }}>{alertError}</p>
            <button onClick={() => setAlertError(null)}>Entendido</button>
          </div>
        </div>
      )}

      {/* Input oculto para subir archivos */}
      <input
        key={fileInputKey}
        type="file"
        accept="image/*"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleUploadFoto}
      />
    </div>
  );
};

export default BarberosPage;