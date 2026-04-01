import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useAuthContext } from "../../../auth/AuthContext";
import { getGanancias } from "../../../services/estadisticas";
import API_URL from "../../../services/api";
import "./EstadisticasPage.css";

const formatMoneda = (n) => {
  try {
    return new Intl.NumberFormat("es-UY", {
      style: "currency",
      currency: "UYU",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Number(n) || 0);
  } catch {
    return `$ ${Number(n) || 0}`;
  }
};

const formatPeriodo = (p, agrupacion) => {
  if (p == null || typeof p !== "string") return String(p ?? "-");
  if (agrupacion === "mes" && /^\d{4}-\d{2}$/.test(p)) {
    const [y, m] = p.split("-");
    const meses = [
      "Ene", "Feb", "Mar", "Abr", "May", "Jun",
      "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
    ];
    return `${meses[parseInt(m, 10) - 1]} ${y}`;
  }
  if (agrupacion === "anio") return p;
  return p;
};

export default function EstadisticasPage() {
  const { user } = useAuthContext();
  const isAdmin = user?.role === "admin";

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [agrupacion, setAgrupacion] = useState("mes");
  const [barberos, setBarberos] = useState([]);
  const [idBarbero, setIdBarbero] = useState("");

  const cargarBarberos = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/barberos/activos`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const list = await res.json();
        setBarberos(list);
      }
    } catch (e) {
      console.warn("No se pudieron cargar barberos", e);
    }
  };

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = {
          agrupacion,
          id_barbero: idBarbero || undefined,
        };
        const res = await getGanancias(params);
        if (!cancelled) setData(res);
      } catch (e) {
        if (!cancelled) setError("No se pudieron cargar las estadísticas.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    run();
    return () => { cancelled = true; };
  }, [agrupacion, idBarbero]);

  useEffect(() => {
    if (isAdmin) cargarBarberos();
  }, [isAdmin]);

  const chartData = Array.isArray(data?.por_periodo)
    ? data.por_periodo.map((p) => ({
        periodo: formatPeriodo(p?.periodo, agrupacion),
        total: Number(p?.total) || 0,
        turnos: Number(p?.cantidad_turnos) || 0,
      }))
    : [];

  const pxPorBarra =
    agrupacion === "dia" ? 118 : agrupacion === "mes" ? 88 : 94;
  const chartMinWidth = Math.max(680, chartData.length * pxPorBarra);
  const barSize =
    agrupacion === "dia" ? 40 : agrupacion === "mes" ? 32 : 36;

  return (
    <div className="estadisticas-page">
      <h1>
        {isAdmin ? "Estadísticas de la barbería" : "Mis ganancias"}
      </h1>

      {/* Filtros */}
      <div className="estadisticas-filtros">
        <div className="estadisticas-agrupacion">
          <label>Agrupar por:</label>
          <select
            value={agrupacion}
            onChange={(e) => setAgrupacion(e.target.value)}
          >
            <option value="dia">Día</option>
            <option value="mes">Mes</option>
            <option value="anio">Año</option>
          </select>
        </div>

        {isAdmin && (
          <div className="estadisticas-barbero">
            <label>Barbero:</label>
            <select
              value={idBarbero}
              onChange={(e) => setIdBarbero(e.target.value)}
            >
              <option value="">Todos</option>
              {barberos.map((b) => (
                <option key={b.id_barbero} value={b.id_barbero}>
                  {b.nombre}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading && <p className="estadisticas-loading">Cargando…</p>}
      {error && <p className="estadisticas-error">{error}</p>}

      {data && !loading && (
        <>
          {/* Resumen rápido */}
          <div className="estadisticas-resumen admin-cards">
            <div className="admin-card success">
              <h3>Hoy</h3>
              <p>{formatMoneda(data.resumen?.hoy)}</p>
            </div>
            <div className="admin-card primary">
              <h3>Este mes</h3>
              <p>{formatMoneda(data.resumen?.este_mes)}</p>
            </div>
            <div className="admin-card">
              <h3>Este año</h3>
              <p>{formatMoneda(data.resumen?.este_anio)}</p>
            </div>
          </div>

          {/* Gráfica */}
          <div className="estadisticas-chart-container">
            <h2>Ganancias por período</h2>
            {chartData.length > 0 ? (
              <div className="estadisticas-chart-scroll">
                <div
                  className="estadisticas-chart-inner"
                  style={{ minWidth: `${chartMinWidth}px`, height: 340 }}
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      barCategoryGap="16%"
                      barGap={1}
                      margin={{ top: 20, right: 20, bottom: 72, left: 24 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                      <XAxis
                        dataKey="periodo"
                        interval={0}
                        tickMargin={12}
                        minTickGap={12}
                        tick={{ fontSize: 12 }}
                        angle={chartData.length > 7 ? -40 : 0}
                        textAnchor={chartData.length > 7 ? "end" : "middle"}
                      />
                      <YAxis
                        width={94}
                        tickFormatter={(v) => formatMoneda(v)}
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip
                        formatter={(value) => formatMoneda(value)}
                        labelFormatter={(label) => `Período: ${label}`}
                      />
                      <Bar
                        dataKey="total"
                        barSize={barSize}
                        fill="#cfa85a"
                        radius={[6, 6, 0, 0]}
                        name="Total"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              <p className="estadisticas-empty">
                No hay datos de ganancias en el período seleccionado.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
