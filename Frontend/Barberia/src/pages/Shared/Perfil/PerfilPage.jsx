import { useAuthContext } from "../../../auth/AuthContext";
import "./PerfilPage.css";

const PerfilPage = () => {
  const { user } = useAuthContext();

  return (
    <div className="perfil-page">
      <h2 className="perfil-title">Mi perfil</h2>

      <form className="perfil-form">
        <div className="perfil-field">
          <label>Nombre</label>
          <input defaultValue={user?.nombre} />
        </div>

        <div className="perfil-field">
          <label>Apellido</label>
          <input defaultValue={user?.apellido} />
        </div>

        <div className="perfil-field">
          <label>Email</label>
          <input defaultValue={user?.email} />
        </div>

        <div className="perfil-field">
          <label>Nueva contraseña</label>
          <input type="password" />
        </div>

        <button className="perfil-btn">Guardar cambios</button>
      </form>
    </div>
  );
};

export default PerfilPage;
