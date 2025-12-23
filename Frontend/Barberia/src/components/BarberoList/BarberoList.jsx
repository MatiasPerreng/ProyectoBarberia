import { useEffect, useState } from "react";
import Footer from "../Footer/Footer";
import "./BarberoList.css";

const BarberosList = ({ onSelectBarbero }) => {
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/barberos/")
      .then(res => res.json())
      .then(data => setBarberos(data))
      .catch(err => console.error(err));
  }, []);

  const handleSelect = (barbero) => {
    setBarberoSeleccionado(barbero);
    onSelectBarbero(barbero);
  };

  return (
    <>
      <div className="booking-overlay">
        <div className="booking-container">

          {/* HEADER (Antes Sidebar) */}
          <aside className="booking-sidebar">
            <div className="logo">
              {/* Ajustá tu ruta de imagen */}
              <img src="/logo.jpg" alt="King Barber" />
            </div>

            <ul className="steps">
              <li className="step done">
                <span className="step-number">✓</span>
                <span className="step-label">Servicio</span>
              </li>
              <li className="step active">
                <span className="step-number">2</span>
                <span className="step-label">Personal</span>
              </li>
              <li className="step">
                <span className="step-number">3</span>
                <span className="step-label">Fecha y hora</span>
              </li>
              <li className="step">
                <span className="step-number">4</span>
                <span className="step-label">Información</span>
              </li>
            </ul>

            {/* Este footer lo ocultaremos en mobile */}
            <div className="sidebar-footer desktop-only">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENIDO LISTA */}
          <section className="booking-content">
            <h3>Seleccionar personal</h3>

            <div className="barberos-grid">
              {barberos.map(barbero => (
                <div
                  key={barbero.id_barbero}
                  className={`barbero-card ${barberoSeleccionado?.id_barbero === barbero.id_barbero ? "selected" : ""
                    }`}
                  onClick={() => handleSelect(barbero)}
                >
                  <div className="avatar">
                    <img src="/barbero-placeholder.png" alt={barbero.nombre} />
                  </div>

                  <div className="barbero-info">
                    <h4>{barbero.nombre}</h4>
                    <span>barbero</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </div>
      </div>
      <Footer />
    </>
  );
};

export default BarberosList;