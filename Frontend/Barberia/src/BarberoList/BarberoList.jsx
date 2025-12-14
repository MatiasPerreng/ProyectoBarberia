import { useEffect, useState } from 'react';

const BarberosList = ({ onSelectBarbero }) => {
  const [barberos, setBarberos] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/barberos/')
      .then(res => res.json())
      .then(data => setBarberos(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="container mt-4">
      <h3>Elegí el barbero</h3>

      <button
        className="btn btn-outline-secondary mb-3"
        onClick={() => onSelectBarbero(null)}
      >
        Sin preferencia
      </button>

      <ul className="list-group">
        {barberos.map(barbero => (
          <li
            key={barbero.id_barbero}
            className="list-group-item list-group-item-action"
            onClick={() => onSelectBarbero(barbero)}
            style={{ cursor: 'pointer' }}
          >
            {barbero.nombre}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BarberosList;
