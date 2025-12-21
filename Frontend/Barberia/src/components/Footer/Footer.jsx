export default function Footer() {
  return (
    <footer className="bg-dark text-light text-center py-3">
      <small>
        © {new Date().getFullYear()} · Developed by <strong>Matias Perreng</strong>
      </small>
    </footer>
  );
}
