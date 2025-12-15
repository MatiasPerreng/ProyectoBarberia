import { useNavigate } from 'react-router-dom';
import Lobby from '../../components/Lobby/Lobby';

export default function LobbyPage() {
  const navigate = useNavigate();

  return (
    <Lobby onAgendaClick={() => navigate('/agenda')} />
  );
}
