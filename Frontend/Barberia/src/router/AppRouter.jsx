import { Routes, Route } from "react-router-dom";

/* =========================
   PUBLIC
========================= */
import HomePage from "../pages/Public/Homepage/Homepage";
import AgendaPage from "../pages/Public/AgendaPage";

/* =========================
   BARBERO
========================= */
import LoginBarbero from "../pages/Barber/LoginBarbero";
import BarberAgenda from "../pages/Barber/BarberAgenda";
import ProtectedRoute from "./ProtectedRoute";

/* =========================
   ADMIN
========================= */
import AdminDashboard from "../pages/Admin/AdminDashboard/AdminDashboard";
import BarberosPage from "../pages/Admin/BarberosPage";
import HorariosPage from "../pages/Admin/HorarioPage/HorariosPage";

export default function AppRouter() {
  return (
    <Routes>
      {/* =========================
         PUBLICAS
      ========================= */}
      <Route path="/" element={<HomePage />} />
      <Route path="/agenda" element={<AgendaPage />} />

      {/* =========================
         BARBERO
      ========================= */}
      <Route path="/login-barbero" element={<LoginBarbero />} />

      <Route
        path="/barbero/agenda"
        element={
          <ProtectedRoute>
            <BarberAgenda />
          </ProtectedRoute>
        }
      />

      {/* =========================
         ADMIN
         (por ahora SIN auth)
      ========================= */}
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/barberos" element={<BarberosPage />} />
      <Route path="/admin/horarios" element={<HorariosPage />} />
    </Routes>
  );
}
