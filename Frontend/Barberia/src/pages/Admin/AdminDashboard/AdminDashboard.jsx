import AdminLayout from "../../../components/Admin/AdminLayout/AdminLayout";
import Footer from "../../../components/Footer/Footer";
import "./AdminDashboard.css";

const AdminDashboard = () => {
  return (
    <>
      <AdminLayout>
        <h1>Dashboard</h1>

        <div className="admin-cards">
          <div className="admin-card">
            <h3>Barberos</h3>
            <p>3 activos</p>
          </div>

          <div className="admin-card">
            <h3>Turnos hoy</h3>
            <p>5</p>
          </div>

          <div className="admin-card">
            <h3>Pendientes</h3>
            <p>2</p>
          </div>
        </div>
      </AdminLayout>

      <Footer />
    </>
  );
};

export default AdminDashboard;
