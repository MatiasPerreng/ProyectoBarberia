import "./AdminHeader.css";

const AdminHeader = ({ title, actionLabel, onAction }) => {
  return (
    <div className="admin-header">
      <h2>{title}</h2>

      {actionLabel && (
        <button onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default AdminHeader;
