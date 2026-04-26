import { useState, useEffect } from "react";
import { listPersonas, updatePersona } from "../api";

export default function PersonasPage() {
  const [personas, setPersonas] = useState([]);
  const [editing, setEditing] = useState(null);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    listPersonas()
      .then(setPersonas)
      .catch(() => setError("Failed to load personas"))
      .finally(() => setLoading(false));
  }, []);

  function startEdit(p) {
    setEditing(p.category);
    setDraft(p.prompt_template);
    setSuccess("");
    setError("");
  }

  function cancelEdit() {
    setEditing(null);
    setDraft("");
  }

  async function saveEdit() {
    setSaving(true);
    setError("");
    try {
      const updated = await updatePersona(editing, { prompt_template: draft });
      setPersonas((prev) => prev.map((p) => (p.category === editing ? updated : p)));
      setSuccess(`${editing} persona updated (v${updated.version})`);
      setEditing(null);
      setDraft("");
    } catch (err) {
      setError(err.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-bold text-slate-800 mb-6">Persona Editor</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">{error}</div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg p-3 mb-4 text-sm">{success}</div>
      )}

      <div className="space-y-4">
        {personas.map((p) => (
          <div key={p.category} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-base font-semibold text-slate-800 capitalize">{p.category} Specialist</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Version {p.version} · Last updated {new Date(p.updated_at).toLocaleString()}
                </p>
              </div>
              {editing === p.category ? (
                <div className="flex gap-2">
                  <button
                    onClick={cancelEdit}
                    className="px-3 py-1.5 text-sm border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={saveEdit}
                    disabled={saving}
                    className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {saving ? "Saving…" : "Save"}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => startEdit(p)}
                  className="px-3 py-1.5 text-sm border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50"
                >
                  Edit
                </button>
              )}
            </div>

            {editing === p.category ? (
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                rows={14}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"
              />
            ) : (
              <pre className="text-xs text-slate-600 whitespace-pre-wrap font-mono bg-slate-50 rounded-lg p-3 max-h-40 overflow-y-auto">
                {p.prompt_template}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
