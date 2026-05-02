import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

// HTTPS local: Mercado Pago exige back_urls en https (desde ~2025).
// Abrí https://localhost:5174 (el navegador avisará certificado de prueba → continuar).
export default defineConfig({
  plugins: [react(), basicSsl()],
  server: {
    host: true,
    port: 5174,
    // Cualquier host (IP pública, LAN, DDNS) para abrir el dev server por URL externa
    allowedHosts: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  }
})
