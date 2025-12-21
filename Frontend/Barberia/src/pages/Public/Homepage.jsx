import Navbar from "../../components/Navbar/Navbar";
import ServiciosList from "../../components/ServiceList/ServiceList";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();

  const handleServicioSelect = (servicio) => {
    // vamos a agenda pero ya con el servicio elegido
    navigate("/agenda", {
      state: { servicio }
    });
  };

  return (
    <>
      <Navbar />

      <div className="container mt-4">
        <h2 className="mb-4">Nuestros servicios</h2>

        <ServiciosList onSelectServicio={handleServicioSelect} />
      </div>
    </>
  );
}
