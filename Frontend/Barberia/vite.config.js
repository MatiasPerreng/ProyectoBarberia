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
    // Incluir IP pública/LAN para acceder desde otro dispositivo o por red
    allowedHosts: [
      "kingbarber.webhop.net",
      "167.62.232.17",
      "186.53.205.51",
      "179.27.203.212",
      "localhost",
      "127.0.0.1",
    ],
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  }
})
