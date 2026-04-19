import { Component } from "react";

/**
 * Evita pantalla en blanco ante errores de render en hijos; permite reintentar.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary:", error, info?.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "50vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "2rem",
            fontFamily: "system-ui, sans-serif",
          }}
        >
          <div style={{ maxWidth: 420, textAlign: "center" }}>
            <h1 style={{ fontSize: "1.25rem", marginBottom: "0.75rem" }}>
              Algo salió mal
            </h1>
            <p style={{ color: "#555", marginBottom: "1.25rem", lineHeight: 1.5 }}>
              Ocurrió un error inesperado al mostrar esta página. Podés volver al inicio o
              reintentar.
            </p>
            <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center" }}>
              <button
                type="button"
                onClick={this.handleReset}
                style={{
                  padding: "0.5rem 1rem",
                  cursor: "pointer",
                  borderRadius: 6,
                  border: "1px solid #ccc",
                  background: "#fff",
                }}
              >
                Reintentar
              </button>
              <a
                href="/"
                style={{
                  padding: "0.5rem 1rem",
                  borderRadius: 6,
                  background: "#111",
                  color: "#fff",
                  textDecoration: "none",
                  display: "inline-block",
                }}
              >
                Ir al inicio
              </a>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
