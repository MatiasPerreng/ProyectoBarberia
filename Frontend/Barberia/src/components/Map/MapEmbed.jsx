export default function MapEmbed() {
  return (
    <div style={{ width: "100%", height: "400px" }}>
      <iframe
        title="Ubicación barbería"
        src="https://maps.app.goo.gl/Nuc3LwmPGw7rcFnq5"
        width="100%"
        height="100%"
        style={{ border: 0 }}
        allowFullScreen=""
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
      ></iframe>
    </div>
  );
}
