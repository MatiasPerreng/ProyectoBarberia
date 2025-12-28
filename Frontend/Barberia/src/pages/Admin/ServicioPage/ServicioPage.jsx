import { useEffect, useState } from "react";
import AdminLayout from "../../../components/Admin/AdminLayout/AdminLayout";
import ServicioCard from "../../../components/Admin/ServicioCard/ServicioCard";
import ServicioForm from "../../../components/Admin/ServicioForm/ServicioForm";
import AdminHeader from "../AdminHeader/AdminHeader";
import {
  getServicios,
  createServicio,
  updateServicio,
  deleteServicio,
} from "../../../services/servicios";

import "./ServicioPage.css";

const ServicioPage = () => {
  const [servicios, setServicios] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [editingServicio, setEditingServicio] = useState(null);

  const fetchServicios = async () => {
    try {
      const data = await getServicios();
      setServicios(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error cargando servicios", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServicios();
  }, []);

  const handleCreate = () => {
    setEditingServicio(null);
    setShowForm(true);
  };

  const handleEdit = (servicio) => {
    setEditingServicio(servicio);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    try {
      await deleteServicio(id);
      fetchServicios();
    } catch (err) {
      console.error("Error eliminando servicio", err);
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingServicio) {
        await updateServicio(editingServicio.id_servicio, formData);
      } else {
        await createServicio(formData);
      }

      setShowForm(false);
      setEditingServicio(null);
      fetchServicios();
    } catch (err) {
      console.error("Error guardando servicio", err);
    }
  };

  return (
    <AdminLayout>
      <AdminHeader
        title="Servicios"
        actionLabel="Agregar servicio"
        onAction={handleCreate}
      />

      {loading && (
        <p className="servicios-page-loading">
          Cargando servicios…
        </p>
      )}

      {!loading && servicios.length === 0 && (
        <p className="servicios-page-empty">
          No hay servicios cargados
        </p>
      )}

      {!loading && servicios.length > 0 && (
        <section className="servicios-page-section">
          <div className="servicios-page-grid">
            {servicios.map((servicio) => (
              <ServicioCard
                key={servicio.id_servicio}
                servicio={servicio}
                onEdit={() => handleEdit(servicio)}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </section>
      )}

      {showForm && (
        <ServicioForm
          servicioInicial={editingServicio}
          onSubmit={handleSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditingServicio(null);
          }}
        />
      )}
    </AdminLayout>
  );
};

export default ServicioPage;
