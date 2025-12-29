import { useEffect, useRef, useState } from "react";
import AdminLayout from "../../../components/Admin/AdminLayout/AdminLayout";
import BarberoForm from "../../../components/Admin/BarberoForm/BarberoForm";
import Footer from "../../../components/Footer/Footer";
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

  /* =========================
     FOTO
  ========================= */
  const fileInputRef = useRef(null);
  const [fileInputKey, setFileInputKey] = useState(0);
  const [barberoFotoTargetId, setBarberoFotoTargetId] = useState(null);

  /* =========================
     CREAR ACCESO (por ID)
  ========================= */
  const [accountTargetId, setAccountTargetId] = useState(null);
  const [accountForm, setAccountForm] = useState({
    email: "",
    password: "",
    rol: "barbero",
  });

  const accountTarget = barberos.find(
    (b) => b.id_barbero === accountTargetId
  );

  /* =========================
     LOAD BARBEROS
  ========================= */
  const loadBarberos = async () => {
    try {
      const data = await getBarberos();

      // ⚠️ IMPORTANTE:
      // mantenemos _fotoUpdatedAt si ya existía
      setBarberos((prev) =>
        data.map((b) => {
          const prevB = prev.find((p) => p.id_barbero === b.id_barbero);
          return {
            ...b,
            _fotoUpdatedAt: prevB?._fotoUpdatedAt,
          };
        })
      );
    } catch {
      setError("No se pudieron cargar los barberos");
    }
  };

  useEffect(() => {
    loadBarberos();
  }, []);

  /* =========================
     CREAR BARBERO
  ========================= */
  const handleCreate = async (data) => {
    return await crearBarbero(data);
  };

  /* =========================
     TOGGLE ACTIVO
  ========================= */
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

  /* =========================
     ELIMINAR
  ========================= */
  const handleDelete = async (barbero) => {
    try {
      await eliminarBarbero(barbero.id_barbero);
      loadBarberos();
    } catch (err) {
      setAlertError(err.message);
    }
  };

  /* =========================
     CAMBIAR FOTO (FIX REAL)
  ========================= */
  const handleSelectFoto = (barbero) => {
    setBarberoFotoTargetId(barbero.id_barbero);
    setFileInputKey((k) => k + 1);

    setTimeout(() => {
      fileInputRef.current?.click();
    }, 0);
  };

  const handleUploadFoto = async (e) => {
    const file = e.target.files[0];
    if (!file || !barberoFotoTargetId) return;

    await subirFotoBarbero(barberoFotoTargetId, file);

    // 🔥 ACTUALIZAMOS SOLO ESE BARBERO
    setBarberos((prev) =>
      prev.map((b) =>
        b.id_barbero === barberoFotoTargetId
          ? {
              ...b,
              _fotoUpdatedAt: Date.now(),
            }
          : b
      )
    );

    setBarberoFotoTargetId(null);
  };

  /* =========================
     CREAR ACCESO (ESTABLE)
  ========================= */
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
    setAccountForm({
      email: "",
      password: "",
      rol: "barbero",
    });

    loadBarberos();
  };

  return (
    <>
      <AdminLayout>
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
                    ? `${API_URL}${b.foto_url}?v=${b._fotoUpdatedAt || 0}`
                    : "/avatar-placeholder.png"
                }
                alt={b.nombre}
              />

              <div className="barberos-info">
                <strong>{b.nombre}</strong>
              </div>

              <div className="barberos-actions">
                <span
                  className={`barberos-status ${
                    b.activo ? "active" : "inactive"
                  }`}
                >
                  {b.activo ? "Activo" : "Inactivo"}
                </span>

                {!b.tiene_usuario && (
                  <button onClick={() => setAccountTargetId(b.id_barbero)}>
                    Crear acceso
                  </button>
                )}

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

        {/* MODAL CREAR ACCESO */}
        {accountTarget && (
          <div className="barberos-access-modal-overlay">
            <div className="barberos-access-modal-card">
              <h3>Crear acceso</h3>
              <p>
                Barbero: <strong>{accountTarget.nombre}</strong>
              </p>

              <form onSubmit={handleCreateAccount}>
                <input
                  type="email"
                  placeholder="Email"
                  required
                  value={accountForm.email}
                  onChange={(e) =>
                    setAccountForm({
                      ...accountForm,
                      email: e.target.value,
                    })
                  }
                />

                <input
                  type="password"
                  placeholder="Contraseña"
                  required
                  value={accountForm.password}
                  onChange={(e) =>
                    setAccountForm({
                      ...accountForm,
                      password: e.target.value,
                    })
                  }
                />

                <select
                  value={accountForm.rol}
                  onChange={(e) =>
                    setAccountForm({
                      ...accountForm,
                      rol: e.target.value,
                    })
                  }
                >
                  <option value="barbero">Barbero</option>
                  <option value="admin">Admin</option>
                </select>

                <div className="barberos-access-modal-actions">
                  <button
                    type="button"
                    onClick={() => setAccountTargetId(null)}
                  >
                    Cancelar
                  </button>
                  <button type="submit">Crear</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {alertError && (
          <div className="modal-overlay">
            <div className="modal-card">
              <h3>No se puede eliminar</h3>
              <p style={{ textAlign: "center" }}>{alertError}</p>
              <button onClick={() => setAlertError(null)}>Entendido</button>
            </div>
          </div>
        )}

        <input
          key={fileInputKey}
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
