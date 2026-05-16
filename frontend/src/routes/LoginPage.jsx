import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const DEMO_ACCOUNTS = [
  { email: "admin@supporttriangle.com", password: "admin123", role: "Admin", color: "bg-purple-100 text-purple-800" },
  { email: "senior@supporttriangle.com", password: "senior123", role: "Senior", color: "bg-blue-100 text-blue-800" },
  { email: "billing@supporttriangle.com", password: "billing123", role: "Billing", color: "bg-green-100 text-green-800" },
  { email: "technical@supporttriangle.com", password: "technical123", role: "Technical", color: "bg-yellow-100 text-yellow-800" },
  { email: "refund@supporttriangle.com", password: "refund123", role: "Refund", color: "bg-red-100 text-red-800" },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/tickets", { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      const status = err.response?.status;
      if (detail) {
        setError(Array.isArray(detail) ? detail[0]?.msg : detail);
      } else if (status) {
        setError(`Server error (HTTP ${status}). Check Vercel environment variables.`);
      } else {
        setError("Cannot reach the server. Check your deployment configuration.");
      }
    } finally {
      setLoading(false);
    }
  }

  function fillCredentials(account) {
    setEmail(account.email);
    setPassword(account.password);
    setError("");
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-gray-800 mb-1">SupportTriangle</h1>
        <p className="text-sm text-gray-500 mb-6">Sign in to your account</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-gray-100">
          <p className="text-xs font-medium text-gray-500 mb-2">Demo accounts — click to fill</p>
          <div className="space-y-1">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                key={account.email}
                type="button"
                onClick={() => fillCredentials(account)}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-left group"
              >
                <div>
                  <span className="text-xs font-medium text-gray-700">{account.email}</span>
                  <span className="text-xs text-gray-400 ml-2">{account.password}</span>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${account.color}`}>
                  {account.role}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
