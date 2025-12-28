import { Routes, Route } from "react-router-dom";

import HomePage from "../pages/Public/Homepage/Homepage";
import AgendaPage from "../pages/Public/AgendaPage";
import LoginBarbero from "../pages/Public/Homepage/LoginBarbero/LoginBarbero";

import BarberAgenda from "../pages/Barber/BarberAgenda";
import BarberoDashboard from "../pages/Barbero/BarberoDashboard";
import BarberoLayout from "../components/Barbero/BarberoLayout/BarberoLayout";

import AdminDashboard from "../pages/Admin/AdminDashboard/AdminDashboard";
import BarberosPage from "../pages/Admin/BarberosPage";
import HorariosPage from "../pages/Admin/HorarioPage/HorariosPage";
import ServicioPage from "../pages/Admin/ServicioPage/ServicioPage";

import ProtectedRoute from "../router/ProtectedRoute";

export default function AppRouter() {
  console.log("🟡 AppRouter render");

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/agenda" element={<AgendaPage />} />
      <Route path="/login-barbero" element={<LoginBarbero />} />

      <Route
        path="/barbero"
        element={
          <ProtectedRoute role="barbero">
            <BarberoLayout>
              <BarberoDashboard />
            </BarberoLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/barbero/agenda"
        element={
          <ProtectedRoute role="barbero">
            <BarberoLayout>
              <BarberAgenda />
            </BarberoLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin"
        element={
          <ProtectedRoute role="admin">
            <AdminDashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/barberos"
        element={
          <ProtectedRoute role="admin">
            <BarberosPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/horarios"
        element={
          <ProtectedRoute role="admin">
            <HorariosPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/servicios"
        element={
          <ProtectedRoute role="admin">
            <ServicioPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
