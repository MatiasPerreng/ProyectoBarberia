import { Routes, Route } from 'react-router-dom'

import LobbyPage from '../pages/Public/LobbyPage'
import AgendaPage from '../pages/Public/AgendaPage'

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<LobbyPage />} />
      <Route path="/agenda" element={<AgendaPage />} />
    </Routes>
  )
}
