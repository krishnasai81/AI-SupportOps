
import { useEffect, useState } from "react";
import {
  Plus,
  RefreshCw,
  Bot,
  Search,
  Ticket,
  Loader2,
  X,
  Eye,
} from "lucide-react";

import {
  getTickets,
  createTicket,
  processTicket,
  getTicket,
} from "../services/api";

const initialForm = {
  customer_name: "",
  customer_email: "",
  subject: "",
  description: "",
};

function StatusBadge({ status }) {
  const styles = {
    open: "bg-blue-50 text-blue-700",
    in_progress: "bg-indigo-50 text-indigo-700",
    waiting_for_human: "bg-amber-50 text-amber-700",
    resolved: "bg-emerald-50 text-emerald-700",
    closed: "bg-slate-100 text-slate-600",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        styles[status] || "bg-slate-100 text-slate-600"
      }`}
    >
      {(status || "unknown").replaceAll("_", " ")}
    </span>
  );
}

function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [processingId, setProcessingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(initialForm);
  const [notice, setNotice] = useState(null);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [agentResult, setAgentResult] = useState(null);

  async function loadTickets() {
    setLoading(true);
    setNotice(null);

    try {
      const data = await getTickets();
      setTickets(Array.isArray(data) ? data : []);
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTickets();
  }, []);

  function updateForm(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }

  async function handleCreateTicket(event) {
    event.preventDefault();
    setCreating(true);
    setNotice(null);

    try {
      const created = await createTicket(form);

      setNotice({
        type: "success",
        message: `Ticket #${created.id} created successfully.`,
      });

      setForm(initialForm);
      setShowForm(false);
      await loadTickets();
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setCreating(false);
    }
  }

  async function handleProcessTicket(ticketId) {
    setProcessingId(ticketId);
    setNotice(null);
    setAgentResult(null);

    try {
      const result = await processTicket(ticketId);

      setAgentResult(result);
      setNotice({
        type: "success",
        message: `AI workflow completed for ticket #${ticketId}.`,
      });

      await loadTickets();
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    } finally {
      setProcessingId(null);
    }
  }

  async function handleViewTicket(ticketId) {
    try {
      const ticket = await getTicket(ticketId);
      setSelectedTicket(ticket);
    } catch (error) {
      setNotice({ type: "error", message: error.message });
    }
  }

  const filteredTickets = tickets.filter((ticket) => {
    const query = search.toLowerCase();

    return (
      String(ticket.id).includes(query) ||
      ticket.subject?.toLowerCase().includes(query) ||
      ticket.category?.toLowerCase().includes(query) ||
      ticket.status?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Ticket Management</h2>
          <p className="mt-1 text-sm text-slate-500">
            Create, track and process customer support tickets.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={loadTickets}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            <RefreshCw size={16} />
            Refresh
          </button>

          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            <Plus size={17} />
            Create Ticket
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

      {showForm && (
        <form
          onSubmit={handleCreateTicket}
          className="space-y-4 rounded-xl border border-slate-200 bg-white p-6"
        >
          <div className="flex items-center justify-between">
            <h3 className="font-bold">Create New Ticket</h3>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="text-slate-400 hover:text-slate-700"
            >
              <X size={20} />
            </button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              label="Customer Name"
              name="customer_name"
              value={form.customer_name}
              onChange={updateForm}
              placeholder="Enter customer name"
            />

            <FormField
              label="Customer Email"
              name="customer_email"
              type="email"
              value={form.customer_email}
              onChange={updateForm}
              placeholder="customer@example.com"
            />

            <div className="sm:col-span-2">
              <FormField
                label="Subject"
                name="subject"
                value={form.subject}
                onChange={updateForm}
                placeholder="Describe the issue briefly"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="mb-2 block text-sm font-medium">
                Description
              </label>
              <textarea
                required
                minLength={10}
                name="description"
                value={form.description}
                onChange={updateForm}
                rows={4}
                placeholder="Explain the customer's issue..."
                className="w-full rounded-lg border border-slate-200 p-3 text-sm outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <button
            disabled={creating}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          >
            {creating && <Loader2 className="animate-spin" size={16} />}
            {creating ? "Creating..." : "Create Ticket"}
          </button>
        </form>
      )}

      <div className="grid gap-3 sm:grid-cols-3">
        <MiniStat title="Total Tickets" value={tickets.length} />
        <MiniStat
          title="Open Tickets"
          value={tickets.filter((t) => t.status === "open").length}
        />
        <MiniStat
          title="Waiting for Review"
          value={
            tickets.filter((t) => t.status === "waiting_for_human").length
          }
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-5">
          <div>
            <h3 className="font-bold">All Tickets</h3>
            <p className="mt-1 text-xs text-slate-500">
              Records retrieved from your FastAPI backend
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2">
            <Search size={16} className="text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search tickets..."
              className="w-40 text-sm outline-none"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center p-12">
            <Loader2 className="animate-spin text-indigo-600" />
          </div>
        ) : filteredTickets.length === 0 ? (
          <div className="p-12 text-center">
            <Ticket className="mx-auto mb-3 text-slate-300" size={35} />
            <p className="font-medium">No tickets found</p>
            <p className="mt-1 text-sm text-slate-500">
              Create a ticket or change your search.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-4">Ticket</th>
                  <th className="px-5 py-4">Category</th>
                  <th className="px-5 py-4">Priority</th>
                  <th className="px-5 py-4">Status</th>
                  <th className="px-5 py-4">Created</th>
                  <th className="px-5 py-4">Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {filteredTickets.map((ticket) => (
                  <tr key={ticket.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4">
                      <p className="font-semibold">{ticket.subject}</p>
                      <p className="mt-1 text-xs text-slate-400">
                        #{ticket.id} · Customer {ticket.customer_id}
                      </p>
                    </td>

                    <td className="px-5 py-4 capitalize">
                      {ticket.category}
                    </td>

                    <td className="px-5 py-4 capitalize">
                      {ticket.priority}
                    </td>

                    <td className="px-5 py-4">
                      <StatusBadge status={ticket.status} />
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-500">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleViewTicket(ticket.id)}
                          title="View ticket"
                          className="rounded-lg border border-slate-200 p-2 hover:bg-slate-100"
                        >
                          <Eye size={16} />
                        </button>

                        <button
                          onClick={() => handleProcessTicket(ticket.id)}
                          disabled={processingId !== null}
                          title="Process with AI"
                          className="rounded-lg bg-indigo-50 p-2 text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
                        >
                          {processingId === ticket.id ? (
                            <Loader2 size={16} className="animate-spin" />
                          ) : (
                            <Bot size={16} />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedTicket && (
        <div className="rounded-xl border border-indigo-100 bg-white p-6">
          <div className="mb-4 flex justify-between">
            <h3 className="font-bold">Ticket #{selectedTicket.id}</h3>
            <button
              onClick={() => setSelectedTicket(null)}
              className="text-slate-400 hover:text-slate-700"
            >
              <X size={20} />
            </button>
          </div>

          <h4 className="font-semibold">{selectedTicket.subject}</h4>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">
            {selectedTicket.description}
          </p>

          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <StatusBadge status={selectedTicket.status} />
            <span className="capitalize text-slate-500">
              {selectedTicket.category} · {selectedTicket.priority}
            </span>
          </div>
        </div>
      )}

      {agentResult !== null && (
        <div className="rounded-xl border border-indigo-200 bg-white p-6">
          <h3 className="mb-3 font-bold">AI Agent Result</h3>
          <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-4 text-xs leading-5 text-emerald-300">
            {JSON.stringify(agentResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function FormField({ label, name, value, onChange, placeholder, type = "text" }) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium">{label}</label>
      <input
        required
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-indigo-500"
      />
    </div>
  );
}

function MiniStat({ title, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}

export default Tickets;
