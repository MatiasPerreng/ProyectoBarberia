import { useEffect, useState } from "react";
import Footer from "../Footer/Footer"; // ajustá la ruta si cambia
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
      {/* BOOKING */}
      <div className="booking-overlay">
        <div className="booking-container">
          <aside className="booking-sidebar">
            <div className="logo">
              <img src="logo.jpg" alt="King Barber" />
            </div>

            <ul className="steps">
              <li className="step done">
                <span>✓</span> Servicio
              </li>
              <li className="step active">
                <span>2</span> Personal
              </li>
              <li className="step">
                <span>3</span> Fecha y hora
              </li>
              <li className="step">
                <span>4</span> Información
              </li>
            </ul>

            <div className="sidebar-footer">
              <p>¿Tenés alguna pregunta?</p>
              <small>099 611 465</small>
            </div>
          </aside>

          {/* CONTENIDO */}
          <section className="booking-content">
            <h3>Seleccionar personal</h3>

            <div className="barberos-grid">
              {barberos.map(barbero => (
                <div
                  key={barbero.id_barbero}
                  className={`barbero-card ${barberoSeleccionado?.id_barbero === barbero.id_barbero
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

                  <h4>{barbero.nombre}</h4>
                  <span>barbero</span>
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
