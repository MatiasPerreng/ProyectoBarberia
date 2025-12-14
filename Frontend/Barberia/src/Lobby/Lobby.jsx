import React from 'react';
import AgendaButton from '../AgendaButton/AgendaButton';
import '../App.css';

const Lobby = ({ onAgendaClick }) => {
  return (
    <div className="lobby-container d-flex flex-column justify-content-center align-items-center">
      <h1 className="lobby-title">King Barber</h1>
      <p className="lobby-subtitle">¡Agendá tu turno acá</p>
      <AgendaButton onClick={onAgendaClick} />
    </div>
  );
};

export default Lobby;
