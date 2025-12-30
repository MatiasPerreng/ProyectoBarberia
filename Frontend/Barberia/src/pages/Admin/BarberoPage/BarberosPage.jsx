import { useEffect, useRef, useState } from "react";
import BarberoForm from "../../../components/Admin/BarberoForm/BarberoForm";
import "./BarberosPage.css";

import {
  getBarberos,
  crearBarbero,
  toggleBarbero,
  subirFotoBarbero,
  eliminarBarbero,
  crearCuentaBarbero,
} from "../../../services/barberos";

import API_URL from "../../../services/api";

const BarberosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const [alertError, setAlertError] = useState(null);

  const fileInputRef = useRef(null);
  const [fileInputKey, setFileInputKey] = useState(0);
  const [barberoFotoTargetId, setBarberoFotoTargetId] = useState(null);

  const [accountTargetId, setAccountTargetId] = useState(null);
  const [accountForm, setAccountForm] = useState({
    email: "",
    password: "",
    rol: "barbero",
  });

  const accountTarget = barberos.find(
    (b) => b.id_barbero === accountTargetId
  );

  const loadBarberos = async () => {
    try {
      const data = await getBarberos();
      setBarberos(data);
    } catch {
      setError("No se pudieron cargar los barberos");
    }
  };

  useEffect(() => {
    loadBarberos();
  }, []);

  const handleCreate = async (data) => {
    await crearBarbero(data);
    loadBarberos();
  };

  const handleToggle = async (barbero) => {
    await toggleBarbero(barbero.id_barbero);
    loadBarberos();
  };

  const handleDelete = async (barbero) => {
    try {
      await eliminarBarbero(barbero.id_barbero);
      loadBarberos();
    } catch (err) {
      setAlertError(err.message);
    }
  };

  const handleSelectFoto = (barbero) => {
    setBarberoFotoTargetId(barbero.id_barbero);
    setFileInputKey((k) => k + 1);
    setTimeout(() => fileInputRef.current?.click(), 0);
  };

  const handleUploadFoto = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    await subirFotoBarbero(barberoFotoTargetId, file);
    loadBarberos();
  };

  const handleCreateAccount = async (e) => {
    e.preventDefault();
    if (!accountTarget) return;

    await crearCuentaBarbero(accountTarget.id_barbero, {
      nombre: accountTarget.nombre,
      email: accountForm.email,
      password: accountForm.password,
      rol: accountForm.rol,
    });

    setAccountTargetId(null);
    loadBarberos();
  };

  return (
    <>
      <div className="barberos-header">
        <h2>Barberos</h2>
        <button
          className="barberos-btn-primary"
          onClick={() => setShowForm(true)}
        >
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
                  ? `${API_URL}${b.foto_url}`
                  : "/avatar-placeholder.png"
              }
              alt={b.nombre}
            />

            <div className="barberos-info">
              <strong>{b.nombre}</strong>
            </div>

            <div className="barberos-actions">
              <button onClick={() => handleToggle(b)}>
                {b.activo ? "Desactivar" : "Activar"}
              </button>

              <button onClick={() => handleSelectFoto(b)}>
                Cambiar foto
              </button>

              <button className="danger" onClick={() => handleDelete(b)}>
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
          onCreated={loadBarberos}
        />
      )}

      <input
        key={fileInputKey}
        type="file"
        accept="image/*"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleUploadFoto}
      />
    </>
  );
};

export default BarberosPage;
