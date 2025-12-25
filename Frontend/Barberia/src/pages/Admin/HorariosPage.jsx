import { useEffect, useState } from "react";
import AdminLayout from "../../components/Admin/AdminLayout/AdminLayout";
import HorarioForm from "../../components/Admin/HorarioForm";
import HorarioList from "../../components/Admin/HorarioList";

import { getBarberos } from "../../services/barberos";
import {
  getHorariosBarbero,
  crearHorario,
  eliminarHorario,
} from "../../services/horarios";

const HorariosPage = () => {
  const [barberos, setBarberos] = useState([]);
  const [barberoSeleccionado, setBarberoSeleccionado] = useState(null);
  const [horarios, setHorarios] = useState([]);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    getBarberos().then(setBarberos);
  }, []);

  useEffect(() => {
    if (barberoSeleccionado) {
      getHorariosBarbero(barberoSeleccionado).then(setHorarios);
    }
  }, [barberoSeleccionado]);

  const handleCreate = async (data) => {
    await crearHorario(data);
    setShowForm(false);
    getHorariosBarbero(barberoSeleccionado).then(setHorarios);
  };

  const handleDelete = async (idHorario) => {
    await eliminarHorario(idHorario);
    getHorariosBarbero(barberoSeleccionado).then(setHorarios);
  };

  return (
    <AdminLayout>
      <div className="admin-page-header">
        <h2>Horarios</h2>

        <select
          onChange={(e) => setBarberoSeleccionado(e.target.value)}
        >
          <option value="">Seleccionar barbero</option>
          {barberos.map((b) => (
            <option key={b.id_barbero} value={b.id_barbero}>
              {b.nombre}
            </option>
          ))}
        </select>

        {barberoSeleccionado && (
          <button onClick={() => setShowForm(true)}>
            + Nuevo horario
          </button>
        )}
      </div>

      {barberoSeleccionado && (
        <HorarioList
          horarios={horarios}
          onDelete={handleDelete}
        />
      )}

      {showForm && (
        <HorarioForm
          idBarbero={barberoSeleccionado}
          onSubmit={handleCreate}
          onClose={() => setShowForm(false)}
        />
      )}
    </AdminLayout>
  );
};

export default HorariosPage;
