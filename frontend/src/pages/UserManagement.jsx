import { ShieldCheck, UserCog } from "lucide-react";
import { useState } from "react";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatDate } from "../utils/format";

const roles = ["Admin", "Analyst"];

export default function UserManagement() {
  const [message, setMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const { data, loading, error, setData } = useApi(async () => (await api.get("/admin/users")).data, []);

  async function changeRole(userId, role) {
    setMessage("");
    setActionError("");
    try {
      const { data: updated } = await api.patch(`/admin/users/${userId}/role`, { role });
      setData(data.map((user) => (user.id === userId ? updated : user)));
      setMessage(`${updated.username} is now ${updated.role}.`);
    } catch (err) {
      setActionError(err.response?.data?.detail || err.message);
    }
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-grid-line bg-white p-6 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-slate-100 text-grid-teal">
            <UserCog size={24} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-grid-ink">User Management</h2>
            <p className="mt-1 text-sm text-slate-500">View platform users and assign Admin or Analyst responsibilities.</p>
          </div>
        </div>
      </section>

      {message && <p className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">{message}</p>}
      {actionError && <ErrorState message={actionError} />}

      <section className="rounded-lg border border-grid-line bg-white shadow-panel">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3">User</th>
                <th className="px-5 py-3">Role</th>
                <th className="px-5 py-3">Created</th>
                <th className="px-5 py-3">Change Role</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-grid-line">
              {data.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50">
                  <td className="px-5 py-4 font-semibold text-grid-ink">{user.username}</td>
                  <td className="px-5 py-4">
                    <span className="inline-flex items-center gap-2 rounded-md bg-slate-100 px-3 py-2 font-semibold text-slate-700">
                      <ShieldCheck size={16} />
                      {user.role}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-slate-500">{formatDate(user.created_at)}</td>
                  <td className="px-5 py-4">
                    <select
                      value={user.role}
                      onChange={(event) => changeRole(user.id, event.target.value)}
                      className="rounded-md border border-grid-line bg-white px-3 py-2 text-sm font-semibold"
                    >
                      {roles.map((role) => <option key={role}>{role}</option>)}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
