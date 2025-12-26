import Navbar from "../../../components/Navbar/Navbar";
import ServiciosList from "../../../components/ServiceList/ServiceList";
import MapEmbed from "../../../components/Map/MapEmbed";
import Footer from "../../../components/Footer/Footer";
import GalleryCarousel from "../../../components/Gallery/GalleryCarousel";
import ContactBar from "../../../components/Contact/ContactBar";
import './Homepage.css'
import { useNavigate } from "react-router-dom";

export default function HomePage() {
    const navigate = useNavigate();

    const handleServicioSelect = (servicio) => {
        navigate("/agenda", { state: { servicio } });
    };

    return (
        <>
            <Navbar />

            {/* HERO */}
            <section className="hero-section">
                <div className="container text-center py-5">
                    <img
                        src="/logo.jpg"
                        alt="King Barber"
                        className="hero-logo mb-4"
                    />

                    <h1 className="display-5 fw-bold">KING BARBER</h1>

                    <p className="lead">
                        Degrades · Barba · Estilo · Reserva online
                    </p>
                    <a href="#servicios" className="btn btn-outline-light">
                        Reservar turno
                    </a>

                </div>
            </section>

            {/* SERVICIOS */}
            <section id="servicios" className="container py-5">
                <h2 className="mb-4 text-center">Nuestros servicios</h2>

                <ServiciosList onSelectServicio={handleServicioSelect} />
            </section>

            <GalleryCarousel />

            {/* MAPA */}
            <section id="ubicacion" className="bg-light py-5">
                <div className="container">
                    <MapEmbed />
                    <ContactBar />
                </div>
            </section>

            <Footer />
        </>
    );
}
