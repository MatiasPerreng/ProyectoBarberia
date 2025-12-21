import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar navbar-dark bg-dark px-3">
      <Link className="navbar-brand" to="/">
        💈 Barbería
      </Link>

      <div>
        <Link className="btn btn-outline-light" to="/login-barbero">
          Soy barbero
        </Link>
      </div>
    </nav>
  );
}
