import { useEffect, useState } from "react";
import Footer from "../Footer/Footer";
import "./BarberoList.css";
import API_URL from "../../services/api";


const BarberosList = ({ onSelectBarbero, onVolver }) => {
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/barberos`)
      .then((res) => res.json())
      .then((data) => setBarberos(data))
      .catch((err) => console.error(err));
  }, []);

  const handleSelect = (barbero) => {
    setBarberoSeleccionado(barbero);
    if (onSelectBarbero) onSelectBarbero(barbero);
  };

  return (
    <>
      <div className="booking-overlay">
        <div className="booking-container">
          <aside className="booking-sidebar">
            <div className="logo">
              <img src="logo.jpg" alt="King Barber" />
            </div>

            <ul className="steps">
              <li className="step done">
                <span className="step-number">✓</span>
                <p className="step-text">Servicio</p>
              </li>
              <li className="step active">
                <span className="step-number">2</span>
                <p className="step-text">Personal</p>
              </li>
              <li className="step">
                <span className="step-number">3</span>
                <p className="step-text">Fecha y hora</p>
              </li>
              <li className="step">
                <span className="step-number">4</span>
                <p className="step-text">Información</p>
              </li>
            </ul>

            <div className="sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          <section className="booking-content">
            {/* BOTÓN VOLVER */}
            <button className="btn-volver" onClick={onVolver}>
              ← Volver
            </button>

            <h3>Seleccionar personal</h3>

            <div className="barberos-grid">
              {barberos.map((barbero) => (
                <div
                  key={barbero.id_barbero}
                  className={`barbero-card ${
                    barberoSeleccionado?.id_barbero === barbero.id_barbero
                      ? "selected"
                      : ""
                  }`}
                  onClick={() => handleSelect(barbero)}
                >
                  <div className="avatar">
                    <img
                      src="/barbero-placeholder.png"
                      alt={barbero.nombre}
                    />
                  </div>

                  <div className="barbero-info">
                    <h4>{barbero.nombre}</h4>
                    <span className="role-text">barbero</span>
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
