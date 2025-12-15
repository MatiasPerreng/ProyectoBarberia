import React from "react";

const AgendaButton = ({ onClick }) => {
  return (
    <button className="btn btn-success btn-lg agenda-button" onClick={onClick}>
      Agendar fecha
    </button>
  );
};

export default AgendaButton;
