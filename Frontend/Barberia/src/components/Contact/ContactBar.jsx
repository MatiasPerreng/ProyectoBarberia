import "./ContactBar.css";

export default function ContactBar() {
  return (
    <div className="contact-card">
      <h3 className="contact-title">Contactanos</h3>
      <p className="contact-subtitle">
        Comunicate con nosotros para cualquier consulta o inquietud.
      </p>

      <div className="contact-divider" />

      {/* DIRECCIÓN */}
      <div className="contact-item">
        <span className="contact-label">
          <span className="contact-icon">📍</span>
          Dirección
        </span>
        <span className="contact-text">
          Egipto 4163, Montevideo, Uruguay
        </span>
      </div>

      <div className="contact-divider" />

      {/* CONTACTO */}
      <div className="contact-item">
        <span className="contact-label">
          <span className="contact-icon">📞</span>
          Contacto
        </span>
        <span className="contact-text">09 961 1465</span>
      </div>

      {/* ICONOS */}
      <div className="contact-socials">
        <a
          href="https://wa.me/59899611465"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="WhatsApp"
        >
          <img src="/icons/whatsapp.svg" alt="WhatsApp" />
        </a>

        <a
          href="https://www.instagram.com/kingbarber"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Instagram"
        >
          <img src="/icons/instagram.svg" alt="Instagram" />
        </a>
      </div>
    </div>
  );
}
