import { Routes, Route } from 'react-router-dom'
import LobbyPage from '../pages/Public/LobbyPage'
import AgendaPage from '../pages/Public/AgendaPage'
import BarberAgenda from "../pages/Barber/BarberAgenda";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<LobbyPage />} />
      <Route path="/agenda" element={<AgendaPage />} />
      <Route path="/barbero/agenda" element={<BarberAgenda />} />
      <Route path="/barber/:barberoId/agenda" element={<BarberAgenda />} />
    </Routes>
  )
}
