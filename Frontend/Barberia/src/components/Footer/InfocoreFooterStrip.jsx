import "./InfocoreFooterStrip.css";
import whatsappIcon from "../../assets/icons/whatsapp.svg";

const INFOCORE_URL = "https://infocore.com.uy";
const INFOCORE_WA_MSISDN = "59897032329";

/** Misma franja que /tv: línea + píldora (Developed by · INFOCORE · web · WhatsApp). */
export default function InfocoreFooterStrip() {
  const year = new Date().getFullYear();

  return (
    <div className="ifs-root">
      <div className="ifs-wrap">
        <span className="ifs-line" aria-hidden="true" />
        <div className="ifs-pill">
          <span className="ifs-label">Developed by</span>
          <span className="ifs-dot" aria-hidden="true" />
          <span className="ifs-name">INFOCORE Solutions</span>
          <span className="ifs-dot" aria-hidden="true" />
          <a
            className="ifs-site"
            href={INFOCORE_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            INFOCORE.COM.UY
          </a>
          <span className="ifs-dot" aria-hidden="true" />
          <a
            className="ifs-wa"
            href={`https://wa.me/${INFOCORE_WA_MSISDN}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img src={whatsappIcon} alt="" className="ifs-wa__icon" width={16} height={16} />
            <span className="ifs-wa__text">Contactanos</span>
          </a>
        </div>
      </div>
      <p className="ifs-rights">All rights reserved © {year}</p>
    </div>
  );
}
