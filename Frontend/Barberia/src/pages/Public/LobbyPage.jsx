import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home">
      <h1>Bienvenido a la barbería</h1>

      <button
        className="btn btn-danger btn-lg"
        onClick={() => navigate("/agenda")}
      >
        Reservar turno
      </button>
    </div>
  );
}
