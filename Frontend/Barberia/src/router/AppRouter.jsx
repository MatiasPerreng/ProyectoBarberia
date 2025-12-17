import { Routes, Route } from "react-router-dom";

import LobbyPage from "../pages/Public/LobbyPage";
import AgendaPage from "../pages/Public/AgendaPage";
import BarberAgenda from "../pages/Barber/BarberAgenda";
import LoginBarbero from "../pages/Barber/LoginBarbero";
import ProtectedRoute from "./ProtectedRoute";

export default function AppRouter() {
  return (
    <Routes>
      {/* PUBLICAS */}
      <Route path="/" element={<LobbyPage />} />
      <Route path="/agenda" element={<AgendaPage />} />
      <Route path="/login-barbero" element={<LoginBarbero />} />

      {/* PRIVADAS BARBERO */}
      <Route
        path="/barbero/agenda"
        element={
          <ProtectedRoute>
            <BarberAgenda />
          </ProtectedRoute>
        }
      />

      <Route
        path="/barber/:barberoId/agenda"
        element={
          <ProtectedRoute>
            <BarberAgenda />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
