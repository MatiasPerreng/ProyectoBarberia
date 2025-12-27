import { useEffect, useState } from "react";
import Footer from "../Footer/Footer";
import "./BarberoList.css";
import API_URL from "../../services/api";

const BarberosList = ({ onSelectBarbero, onVolver }) => {
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/barberos/activos`)
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
      <div className="bl-overlay">
        <div className="bl-container">
          {/* SIDEBAR */}
          <aside className="bl-sidebar">
            <div className="bl-logo">
              <img src="logo.jpg" alt="King Barber" />
            </div>

            <ul className="bl-steps">
              <li className="bl-step done">
                <span className="bl-step-number">✓</span>
                <p className="bl-step-text">Servicio</p>
              </li>

              <li className="bl-step active">
                <span className="bl-step-number">2</span>
                <p className="bl-step-text">Personal</p>
              </li>

              <li className="bl-step">
                <span className="bl-step-number">3</span>
                <p className="bl-step-text">Fecha y hora</p>
              </li>

              <li className="bl-step">
                <span className="bl-step-number">4</span>
                <p className="bl-step-text">Información</p>
              </li>
            </ul>

            <div className="bl-sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENT */}
          <section className="bl-content">
            <button className="bl-btn-volver" onClick={onVolver}>
              ← Volver
            </button>

            <h3>Seleccionar personal</h3>

            <div className="bl-grid">
              {barberos.map((barbero) => (
                <div
                  key={barbero.id_barbero}
                  className={`bl-card ${
                    barberoSeleccionado?.id_barbero === barbero.id_barbero
                      ? "selected"
                      : ""
                  }`}
                  onClick={() => handleSelect(barbero)}
                >
                  <div className="bl-avatar">
                    <img
                      src={
                        barbero.foto_url
                          ? `${API_URL}${barbero.foto_url}`
                          : "/barbero-placeholder.png"
                      }
                      alt={barbero.nombre}
                    />
                  </div>

                  <div className="bl-info">
                    <h4>{barbero.nombre}</h4>
                    <span className="bl-role">barbero</span>
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
