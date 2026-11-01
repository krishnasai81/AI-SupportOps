
import { useEffect, useState } from "react";
import {
  ShieldCheck,
  Lock,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Loader2,
  LogOut,
  Clock,
  AlertCircle,
} from "lucide-react";

import {
  loginApprovals,
  logoutApprovals,
  getPendingApprovals,
  submitApprovalDecision,
} from "../services/api";

function Approvals() {
  const [apiKey, setApiKey] = useState("");
  const [authenticated, setAuthenticated] = useState(false);
  const [approvals, setApprovals] = useState([]);
  const [reviewer, setReviewer] = useState("");
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(false);
  const [decisionId, setDecisionId] = useState(null);
  const [notice, setNotice] = useState(null);

  async function loadApprovals() {
    setLoading(true);

    try {
      const data = await getPendingApprovals();
      setApprovals(Array.isArray(data) ? data : []);
      setAuthenticated(true);
    } catch (error) {
      if (error.response?.status === 401) {
        setAuthenticated(false);
      }

      setNotice({
        type: "error",
        message: error.response?.data?.detail || error.message,
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApprovals();
  }, []);

  async function handleLogin(event) {
    event.preventDefault();
    setLoading(true);
    setNotice(null);

    try {
      await loginApprovals(apiKey);
      setApiKey("");
      setAuthenticated(true);
      await loadApprovals();
      setNotice({
        type: "success",
        message: "Approval access granted.",
      });
    } catch (error) {
      setNotice({
        type: "error",
        message: error.response?.data?.detail || error.message,
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await logoutApprovals();
    } finally {
      setAuthenticated(false);
      setApprovals([]);
      setNotice(null);
    }
  }

  async function handleDecision(approvalId, decision) {
    if (!reviewer.trim()) {
      setNotice({
        type: "error",
        message: "Enter the reviewer name before submitting a decision.",
      });
      return;
    }

    setDecisionId(approvalId);
    setNotice(null);

    try {
      await submitApprovalDecision(approvalId, {
        decision,
        reviewer_name: reviewer.trim(),
        review_note: notes[approvalId] || null,
      });

      setNotice({
        type: "success",
        message: `Approval #${approvalId} was ${decision}d.`,
      });

      await loadApprovals();
    } catch (error) {
      setNotice({
        type: "error",
        message: error.response?.data?.detail || error.message,
      });
    } finally {
      setDecisionId(null);
    }
  }

  if (!authenticated) {
    return (
      <div className="mx-auto max-w-lg rounded-xl border border-slate-200 bg-white p-8">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-lg bg-indigo-50 p-3 text-indigo-600">
            <Lock size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold">Approval Center</h2>
            <p className="text-sm text-slate-500">
              Restricted reviewer access
            </p>
          </div>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <label className="block text-sm font-medium">
            Approval API Key

            <input
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder="Enter your approval key"
              required
              autoComplete="current-password"
              className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-3 outline-none focus:border-indigo-500"
            />
          </label>

          <button
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
          >
            {loading && <Loader2 size={17} className="animate-spin" />}
            Authenticate
          </button>
        </form>

        {notice && (
          <p className="mt-4 text-sm text-red-600">{notice.message}</p>
        )}

        <p className="mt-5 text-xs leading-5 text-slate-400">
          The key is sent to FastAPI for validation and is not saved in
          browser storage.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Human Approval Center</h2>
          <p className="mt-1 text-sm text-slate-500">
            Review sensitive actions before authorization.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={loadApprovals}
            disabled={loading}
            className="rounded-lg border border-slate-200 bg-white p-2.5 hover:bg-slate-50"
            title="Refresh"
          >
            <RefreshCw size={17} />
          </button>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm hover:bg-slate-50"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </div>

      {notice && (
        <div
          className={`rounded-lg border p-3 text-sm ${
            notice.type === "error"
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-700"
          }`}
        >
          {notice.message}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard
          title="Pending Requests"
          value={approvals.length}
          icon={Clock}
        />
        <StatCard
          title="Human Review"
          value="Enabled"
          icon={ShieldCheck}
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="mb-1 font-bold">Pending Requests</h3>
        <p className="mb-5 text-xs text-slate-500">
          Requests retrieved from your approval service.
        </p>

        {loading && approvals.length === 0 ? (
          <div className="flex justify-center p-8">
            <Loader2 className="animate-spin text-indigo-600" />
          </div>
        ) : approvals.length === 0 ? (
          <div className="py-10 text-center">
            <CheckCircle2
              size={35}
              className="mx-auto mb-3 text-emerald-500"
            />
            <p className="font-medium">No pending approvals</p>
            <p className="mt-1 text-sm text-slate-500">
              New requests will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            {approvals.map((item) => (
              <div
                key={item.id}
                className="rounded-xl border border-slate-200 p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h4 className="font-bold">
                      Approval #{item.id}
                    </h4>
                    <p className="mt-1 text-xs text-slate-500">
                      Ticket #{item.ticket_id} · Customer #{item.customer_id}
                    </p>
                  </div>

                  <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
                    {item.status}
                  </span>
                </div>

                <div className="mt-5 space-y-3">
                  <InfoRow label="Action" value={item.action_type} />
                  <InfoRow
                    label="Requested action"
                    value={item.requested_action}
                  />
                  <InfoRow label="Reason" value={item.reason} />
                  <InfoRow
                    label="Created"
                    value={
                      item.created_at
                        ? new Date(item.created_at).toLocaleString()
                        : "Unknown"
                    }
                  />
                </div>

                <div className="mt-5 space-y-3 border-t border-slate-100 pt-5">
                  <label className="block text-sm font-medium">
                    Reviewer Name
                    <input
                      value={reviewer}
                      onChange={(event) => setReviewer(event.target.value)}
                      placeholder="Enter your name"
                      className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-indigo-500"
                    />
                  </label>

                  <label className="block text-sm font-medium">
                    Review Note
                    <textarea
                      value={notes[item.id] || ""}
                      onChange={(event) =>
                        setNotes({
                          ...notes,
                          [item.id]: event.target.value,
                        })
                      }
                      rows={2}
                      placeholder="Add a reason for your decision..."
                      className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-indigo-500"
                    />
                  </label>

                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => handleDecision(item.id, "approve")}
                      disabled={decisionId !== null}
                      className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                    >
                      {decisionId === item.id ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <CheckCircle2 size={16} />
                      )}
                      Approve
                    </button>

                    <button
                      onClick={() => handleDecision(item.id, "reject")}
                      disabled={decisionId !== null}
                      className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                    >
                      <XCircle size={16} />
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-900">
        <AlertCircle size={17} className="mt-0.5 shrink-0" />
        Approval records authorize review decisions only. They do not execute
        refunds, account modifications or subscription changes.
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{title}</p>
        <Icon size={20} className="text-indigo-600" />
      </div>
      <p className="mt-4 text-2xl font-bold">{value}</p>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase text-slate-400">
        {label}
      </p>
      <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">
        {value || "Not provided"}
      </p>
    </div>
  );
}

export default Approvals;
