import { Routes, Route } from "react-router-dom";

/* =========================
   PUBLIC
========================= */
import HomePage from "../pages/Public/Homepage/Homepage";
import AgendaPage from "../pages/Public/AgendaPage";

/* =========================
   BARBERO
========================= */
import LoginBarbero from "../pages/Public/Homepage/LoginBarbero/LoginBarbero";
import BarberAgenda from "../pages/Barber/BarberAgenda";
import BarberoDashboard from "../pages/Barbero/BarberoDashboard";
import BarberoLayout from "../components/Barbero/BarberoLayout/BarberoLayout";
import ProtectedRoute from "../router/ProtectedRoute";

/* =========================
   ADMIN (sin auth por ahora)
========================= */
import AdminDashboard from "../pages/Admin/AdminDashboard/AdminDashboard";
import BarberosPage from "../pages/Admin/BarberosPage";
import HorariosPage from "../pages/Admin/HorarioPage/HorariosPage";
import ServicioPage from "../pages/Admin/ServicioPage/ServicioPage";

export default function AppRouter() {
  return (
    <Routes>
      {/* =========================
         PUBLICAS
      ========================= */}
      <Route path="/" element={<HomePage />} />
      <Route path="/agenda" element={<AgendaPage />} />

      {/* =========================
         LOGIN BARBERO
      ========================= */}
      <Route path="/login-barbero" element={<LoginBarbero />} />

      {/* =========================
         BARBERO (PROTEGIDO)
      ========================= */}
      <Route
        path="/barbero"
        element={
          <ProtectedRoute>
            <BarberoLayout>
              <BarberoDashboard />
            </BarberoLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/barbero/agenda"
        element={
          <ProtectedRoute>
            <BarberoLayout>
              <BarberAgenda />
            </BarberoLayout>
          </ProtectedRoute>
        }
      />

      {/* =========================
         ADMIN (DEV)
      ========================= */}
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/barberos" element={<BarberosPage />} />
      <Route path="/admin/horarios" element={<HorariosPage />} />
      <Route path="/admin/servicios" element={<ServicioPage />} />
    </Routes>
  );
}
