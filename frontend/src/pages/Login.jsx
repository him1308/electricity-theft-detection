import { Lock, Zap } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../services/api";

export default function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-grid-surface px-4">
      <form onSubmit={submit} className="w-full max-w-md rounded-lg border border-grid-line bg-white p-8 shadow-panel">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-grid-ink text-white">
            <Zap size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-grid-ink">GridGuard</h1>
            <p className="text-sm text-slate-500">Smart meter anomaly detection</p>
          </div>
        </div>
        <label className="block text-sm font-semibold text-slate-700">Username</label>
        <input value={username} onChange={(event) => setUsername(event.target.value)} className="mt-2 w-full rounded-md border border-grid-line px-3 py-2.5 outline-none focus:border-grid-teal" />
        <label className="mt-5 block text-sm font-semibold text-slate-700">Password</label>
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-md border border-grid-line px-3 py-2.5 outline-none focus:border-grid-teal" />
        {error && <p className="mt-4 rounded-md bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{error}</p>}
        <button className="mt-6 flex w-full items-center justify-center gap-2 rounded-md bg-grid-ink px-4 py-3 font-semibold text-white hover:bg-slate-800">
          <Lock size={18} />
          Sign in
        </button>
        <p className="mt-4 text-sm text-slate-500">Demo accounts: admin/admin123 or analyst/analyst123</p>
      </form>
    </div>
  );
}
