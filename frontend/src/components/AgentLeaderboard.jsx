export default function AgentLeaderboard({ data }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-4">Agent Leaderboard</h3>
      {data.length === 0 ? (
        <p className="text-sm text-slate-400 text-center py-6">No agent data for this window</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 text-xs text-slate-500 uppercase tracking-wide">
              <th className="text-left pb-2 font-medium">Agent</th>
              <th className="text-left pb-2 font-medium">Role</th>
              <th className="text-right pb-2 font-medium">Handled</th>
              <th className="text-right pb-2 font-medium">Approval %</th>
              <th className="text-right pb-2 font-medium">Avg Edit Dist</th>
            </tr>
          </thead>
          <tbody>
            {data.map((a) => (
              <tr key={a.user_id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="py-2">
                  <div className="font-medium text-slate-800">{a.user_full_name}</div>
                  <div className="text-xs text-slate-400">{a.user_email}</div>
                </td>
                <td className="py-2 text-slate-500 capitalize">{a.role}</td>
                <td className="py-2 text-right font-semibold text-slate-700">{a.tickets_handled}</td>
                <td className="py-2 text-right">
                  <span
                    className={`font-semibold ${
                      a.approval_rate >= 80 ? "text-green-600" : a.approval_rate >= 50 ? "text-amber-600" : "text-red-500"
                    }`}
                  >
                    {a.approval_rate}%
                  </span>
                </td>
                <td className="py-2 text-right text-slate-600">{a.avg_edit_distance.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
