import { useState, useEffect } from "react";
import { getCarouselImages } from "../../services/carousel";
import API_URL from "../../services/api";
import "./GalleryCarousel.css";

export default function GalleryCarousel() {
  const [imagenes, setImagenes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCarouselImages()
      .then((data) => setImagenes(Array.isArray(data) ? data : []))
      .catch(() => setImagenes([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading || imagenes.length === 0) {
    return (
      <section className="gallery-section py-5">
        <div className="container">
          <div className="gallery-title-wrapper">
            <h2 className="gallery-title">
              <span>Nuestros</span> trabajos
            </h2>
            <div className="gallery-title-line" />
          </div>
          {!loading && imagenes.length === 0 && (
            <div className="gallery-empty">Próximamente más trabajos.</div>
          )}
        </div>
      </section>
    );
  }

  return (
    <section className="gallery-section py-5">
      <div className="container">
        <div className="gallery-title-wrapper">
          <h2 className="gallery-title">
            <span>Nuestros</span> trabajos
          </h2>
          <div className="gallery-title-line" />
        </div>

        <div
          id="galleryCarousel"
          className="carousel slide"
          data-bs-ride="carousel"
        >
          <div className="carousel-inner">
            {imagenes.map((img, i) => (
              <div
                key={img.filename}
                className={`carousel-item ${i === 0 ? "active" : ""}`}
              >
                <img
                  src={`${API_URL}${img.url}`}
                  className="d-block w-100 gallery-img"
                  alt={`Trabajo ${i + 1}`}
                />
              </div>
            ))}
          </div>

          {imagenes.length > 1 && (
            <>
              <button
                className="carousel-control-prev"
                type="button"
                data-bs-target="#galleryCarousel"
                data-bs-slide="prev"
              >
                <span className="carousel-control-prev-icon" />
              </button>
              <button
                className="carousel-control-next"
                type="button"
                data-bs-target="#galleryCarousel"
                data-bs-slide="next"
              >
                <span className="carousel-control-next-icon" />
              </button>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
