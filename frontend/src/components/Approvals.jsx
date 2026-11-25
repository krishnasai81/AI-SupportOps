import { useEffect, useState } from "react";
import { ShieldCheck, RefreshCw, CheckCircle2, XCircle, Loader2, Clock, AlertCircle } from "lucide-react";
import { getPendingApprovals, submitApprovalDecision } from "../services/api";

export default function Approvals({ user }) {
  const [approvals, setApprovals] = useState([]);
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(false);
  const [decisionId, setDecisionId] = useState(null);
  const [notice, setNotice] = useState(null);

  async function loadApprovals() {
    setLoading(true);
    try {
      setApprovals(await getPendingApprovals());
      setNotice(null);
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadApprovals(); }, []);

  async function handleDecision(approvalId, decision) {
    setDecisionId(approvalId);
    setNotice(null);
    try {
      await submitApprovalDecision(approvalId, {
        decision,
        review_note: notes[approvalId] || null,
      });
      setNotice({ type: "success", message: `Approval #${approvalId} was ${decision}d by ${user.email}.` });
      await loadApprovals();
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setDecisionId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h2 className="text-2xl font-bold">Human Approval Center</h2><p className="mt-1 text-sm text-slate-500">Signed in as {user.email} · {user.role}</p></div>
        <button onClick={loadApprovals} disabled={loading} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm"><RefreshCw size={16} />Refresh</button>
      </div>
      {notice && <div className={`rounded-lg border p-3 text-sm ${notice.type === "error" ? "border-red-200 bg-red-50 text-red-700" : "border-emerald-200 bg-emerald-50 text-emerald-700"}`}>{notice.message}</div>}
      <div className="grid gap-4 sm:grid-cols-2">
        <Stat title="Pending requests" value={approvals.length} icon={Clock} />
        <Stat title="Access" value="Authorized support staff" icon={ShieldCheck} />
      </div>
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="font-bold">Pending requests</h3>
        {loading && approvals.length === 0 ? <div className="flex justify-center p-10"><Loader2 className="animate-spin text-indigo-600" /></div> : approvals.length === 0 ? <div className="py-10 text-center"><CheckCircle2 size={34} className="mx-auto mb-3 text-emerald-500" /><p className="font-medium">No pending approvals</p></div> : (
          <div className="mt-5 space-y-5">
            {approvals.map(item => <article key={item.id} className="rounded-xl border border-slate-200 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3"><div><h4 className="font-bold">Approval #{item.id}</h4><p className="text-xs text-slate-500">Ticket #{item.ticket_id} · Customer #{item.customer_id}</p></div><span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">{item.status}</span></div>
              <div className="mt-4 space-y-3 text-sm">
                <Info label="Action" value={item.action_type} /><Info label="Requested action" value={item.requested_action} /><Info label="Reason" value={item.reason} />
              </div>
              <label className="mt-5 block text-sm font-medium">Review note<textarea value={notes[item.id] || ""} onChange={e => setNotes({ ...notes, [item.id]: e.target.value })} rows={2} maxLength={1000} className="mt-2 w-full rounded-lg border border-slate-200 p-3" placeholder="Optional reason for your decision" /></label>
              <div className="mt-4 flex gap-3">
                <button onClick={() => handleDecision(item.id, "approve")} disabled={decisionId !== null} className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{decisionId === item.id ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}Approve</button>
                <button onClick={() => handleDecision(item.id, "reject")} disabled={decisionId !== null} className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"><XCircle size={16} />Reject</button>
              </div>
            </article>)}
          </div>
        )}
      </section>
      <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-900"><AlertCircle size={17} className="mt-0.5 shrink-0" />An approval records a human decision; it does not itself execute refunds, account changes or subscription changes.</div>
    </div>
  );
}

function Stat({ title, value, icon: Icon }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between text-sm text-slate-500">{title}<Icon size={19} className="text-indigo-600" /></div><p className="mt-4 text-2xl font-bold">{value}</p></div>;
}
function Info({ label, value }) {
  return <div><p className="text-xs font-semibold uppercase text-slate-400">{label}</p><p className="mt-1 whitespace-pre-wrap text-slate-700">{value || "Not provided"}</p></div>;
}
