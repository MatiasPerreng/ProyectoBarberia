import { useState } from 'react';

const AgendaForm = ({ onSubmit }) => {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [email, setEmail] = useState('');
  const [telefono, setTelefono] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      nombre,
      apellido,
      email,
      telefono
    });
  };

  return (
    <div className="container mt-4">
      <h2>Datos del cliente</h2>

      <form
        onSubmit={handleSubmit}
        className="d-flex flex-column align-items-center"
      >
        <input
          type="text"
          placeholder="Nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="form-control mb-2"
          required
        />

        <input
          type="text"
          placeholder="Apellido"
          value={apellido}
          onChange={(e) => setApellido(e.target.value)}
          className="form-control mb-2"
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="form-control mb-2"
          required
        />

        <input
          type="text"
          placeholder="Teléfono (opcional)"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
          className="form-control mb-3"
        />

        <button type="submit" className="btn btn-success">
          Confirmar turno
        </button>
      </form>
    </div>
  );
};

export default AgendaForm;
