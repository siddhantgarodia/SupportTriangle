import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { format, parseISO } from "date-fns";

export default function TimeSeriesChart({ data }) {
  const formatted = data.map((d) => ({
    ...d,
    label: format(parseISO(d.timestamp), "MMM d HH:mm"),
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-4">Ticket Volume Over Time</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={formatted} margin={{ top: 4, right: 8, left: -20, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            name="Tickets"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
