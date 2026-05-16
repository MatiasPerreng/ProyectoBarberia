import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../../components/Navbar/Navbar";
import ServiciosList from "../../../components/ServiceList/ServiceList";
import MapEmbed from "../../../components/Map/MapEmbed";
import Footer from "../../../components/Footer/Footer";
import GalleryCarousel from "../../../components/Gallery/GalleryCarousel";
import ContactBar from "../../../components/Contact/ContactBar";
import "./Homepage.css";

export default function HomePage() {
  const navigate = useNavigate();

  useEffect(() => {
    const observerOptions = {
      root: null,
      threshold: 0.1,
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("active");
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    const revealSections = document.querySelectorAll(".reveal");
    revealSections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  const handleServicioSelect = (servicio) => {
    navigate("/agenda", { state: { servicio } });
  };

  return (
    <div className="homepage-main-container">
      <Navbar />

      <section className="hero-section">
        <div className="container text-center py-5">
          <img
            src="/logo.jpg"
            alt="King Barber"
            className="hero-logo mb-4"
          />

          <h1 className="display-5 fw-bold hero-title">
            KING BARBER
          </h1>

          <p className="lead">
            Degrades · Barba · Colometría · Reserva online
          </p>

          <a href="#servicios" className="btn btn-outline-light">
            Reservar turno
          </a>
        </div>
      </section>

      <section id="servicios" className="container py-5 reveal">
        <h2 className="services-title mb-4 text-center">Nuestros servicios</h2>
        <ServiciosList onSelectServicio={handleServicioSelect} />
      </section>

      <section id="trabajos" className="reveal">
        <GalleryCarousel />
      </section>

      <section id="ubicacion" className="bg-light pt-5 pb-2 reveal">
        <div className="container">
          <MapEmbed />
        </div>
      </section>

      <section className="cta-strip reveal" aria-label="Pago con Mercado Pago">
        <div className="cta-strip-glow" aria-hidden="true" />
        <div className="cta-strip-grid-pattern" aria-hidden="true" />
        <div className="container cta-strip-container">
          <div className="cta-strip-grid">
            <div className="cta-strip-copy">
              <p className="cta-strip-eyebrow">Agenda online</p>
              <h2 className="cta-strip-title">¿Listo para tu turno?</h2>
              <p className="cta-strip-lead">
                Reservá hoy y asegurá tu lugar con{" "}
                <span className="cta-strip-nowrap">King Barber.</span> Elegí servicio,
                barbero y horario{" "}
                <span className="cta-strip-nowrap">en pocos pasos.</span>
              </p>
              <div className="cta-strip-mp">
                <div className="cta-strip-mp-logo-wrap">
                  <img
                    src="/mercadopago.png"
                    alt="Mercado Pago"
                    className="cta-strip-mp-logo"
                    width={168}
                    height={48}
                    decoding="async"
                  />
                </div>
                <div className="cta-strip-mp-body">
                  <span className="cta-strip-mp-label">Pago anticipado</span>
                  <p className="cta-strip-mp-text">
                    Podés abonar con <strong>Mercado Pago</strong> antes de tu visita.
                    El total incluye un pequeño costo de gestión online; en la reserva
                    ves el monto exacto antes de pagar.
                  </p>
                </div>
              </div>
            </div>
            <div className="cta-strip-aside">
              <a href="#servicios" className="btn-cta-strip">
                Reservar y pagar online
              </a>
            </div>
          </div>
        </div>
      </section>

      <section id="contacto" className="contact-section pt-2 pb-5 reveal">
        <div className="container">
          <ContactBar />
        </div>
      </section>

      <Footer />
    </div>
  );
}
