import { useEffect, useState } from "react";
import {
  Activity, Bot, CheckCircle2, Clock3, LayoutDashboard, MessageSquare,
  BookOpen, ShieldCheck, Settings, Headset, Bell, LogOut, UserRound
} from "lucide-react";

import Tickets from "./components/Tickets";
import { checkBackendConnection, clearAuthSession, getCurrentUser, getSavedUser, hasAuthToken, getTickets } from "./services/api";
import KnowledgeBase from "./components/KnowledgeBase";
import Approvals from "./components/Approvals";
import Auth from "./components/Auth";

function App() {
  const [user, setUser] = useState(() => getSavedUser());
  const [authReady, setAuthReady] = useState(false);
  const [activePage, setActivePage] = useState("Dashboard");
  const [backend, setBackend] = useState({ connected: false });
  const [tickets, setTickets] = useState([]);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!hasAuthToken()) {
      setUser(null);
      setAuthReady(true);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => { clearAuthSession(); setUser(null); })
      .finally(() => setAuthReady(true));
  }, []);

  async function loadDashboard() {
    setChecking(true);
    const [connection, ticketResult] = await Promise.all([
      checkBackendConnection(),
      getTickets().catch(() => []),
    ]);
    setBackend(connection);
    setTickets(Array.isArray(ticketResult) ? ticketResult : []);
    setChecking(false);
  }

  useEffect(() => {
    if (user) loadDashboard();
  }, [user]);

  function logout() {
    clearAuthSession();
    setUser(null);
    setTickets([]);
    setActivePage("Dashboard");
  }

  if (!authReady) {
    return <div className="flex min-h-screen items-center justify-center text-slate-500">Loading your workspace...</div>;
  }
  if (!user) {
    return <Auth onAuthenticated={setUser} />;
  }

  const isStaff = user.role === "support" || user.role === "admin";
  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Tickets", icon: MessageSquare },
    ...(isStaff ? [
      { name: "AI Agents", icon: Bot },
      { name: "Knowledge Base", icon: BookOpen },
      { name: "Approvals", icon: ShieldCheck },
    ] : []),
  ];

  const resolved = tickets.filter(t => t.status === "resolved" || t.status === "closed").length;
  const waiting = tickets.filter(t => t.status === "waiting_for_human").length;
  const open = tickets.filter(t => t.status === "open").length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white p-5 md:flex md:flex-col">
          <div className="mb-10 flex items-center gap-3">
            <div className="rounded-xl bg-indigo-600 p-2 text-white"><Headset size={24} /></div>
            <div><h1 className="text-lg font-bold">SupportOps</h1><p className="text-xs text-slate-500">AI Support Platform</p></div>
          </div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Workspace</p>
          <nav className="space-y-1">
            {navigation.map(item => {
              const Icon = item.icon;
              const selected = activePage === item.name;
              return <button key={item.name} onClick={() => setActivePage(item.name)} className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition ${selected ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-100"}`}>
                <Icon size={18} />{item.name}
              </button>;
            })}
          </nav>
          <div className="mt-auto border-t border-slate-200 pt-4">
            <div className="flex items-center gap-2 px-2 pb-3 text-xs text-slate-500"><UserRound size={15} /><span className="truncate">{user.email}</span></div>
            <div className="mb-3 rounded-md bg-slate-100 px-3 py-2 text-xs font-semibold uppercase text-slate-600">{user.role}</div>
            <button onClick={logout} className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm text-slate-600 hover:bg-slate-100"><LogOut size={18} />Sign out</button>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <header className="flex min-h-20 items-center justify-between border-b border-slate-200 bg-white px-5 py-3 md:px-8">
            <div><h2 className="text-xl font-bold">{activePage}</h2><p className="mt-1 text-xs text-slate-500">AI-powered customer support operations</p></div>
            <div className="flex items-center gap-3">
              <div className="hidden text-right sm:block"><p className="text-sm font-semibold">{user.email}</p><p className="text-xs capitalize text-slate-500">{user.role}</p></div>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700">{user.email?.[0]?.toUpperCase() || "U"}</div>
              <button onClick={logout} title="Sign out" className="rounded-lg border border-slate-200 p-2 text-slate-500 hover:bg-slate-50 md:hidden"><LogOut size={17} /></button>
            </div>
          </header>

          <div className="p-5 md:p-8">
            {activePage === "Tickets" ? <Tickets user={user} onTicketsChanged={loadDashboard} /> :
             activePage === "Knowledge Base" && isStaff ? <KnowledgeBase /> :
             activePage === "Approvals" && isStaff ? <Approvals user={user} /> :
             activePage === "AI Agents" && isStaff ? (
               <div className="rounded-xl border border-slate-200 bg-white p-6"><h3 className="font-bold">Multi-agent workflow</h3><p className="mt-2 text-sm text-slate-600">Classification → Knowledge Retrieval → Supervisor Routing → Troubleshooting → Response Generation → Human Escalation.</p></div>
             ) : (
              <>
                <div className="mb-7 flex flex-wrap items-center justify-between gap-3">
                  <div><h3 className="text-2xl font-bold">Overview</h3><p className="mt-1 text-sm text-slate-500">{isStaff ? "Monitor support operations and pending reviews." : "Track your customer support requests."}</p></div>
                  <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-xs">
                    <span className={`h-2 w-2 rounded-full ${backend.connected ? "bg-emerald-500" : "bg-red-500"}`} />
                    {checking ? "Checking backend..." : backend.connected ? "Backend connected" : "Backend disconnected"}
                  </div>
                </div>
                <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <MetricCard title={isStaff ? "Total Tickets" : "My Tickets"} value={tickets.length} icon={MessageSquare} />
                  <MetricCard title="Resolved Tickets" value={resolved} icon={CheckCircle2} />
                  <MetricCard title="Pending Human Review" value={isStaff ? waiting : tickets.filter(t => t.status === "waiting_for_human").length} icon={Clock3} />
                  <MetricCard title="Open Tickets" value={open} icon={Activity} />
                </section>
                <div className="mt-7 rounded-xl border border-slate-200 bg-white p-6">
                  <h3 className="font-bold">{isStaff ? "Support Operations" : "Your support requests"}</h3>
                  <p className="mt-1 text-sm text-slate-500">{isStaff ? "Manage customer tickets and run the multi-agent workflow." : "Create a ticket in your language and attach a photo of the problem."}</p>
                  <button onClick={() => setActivePage("Tickets")} className="mt-5 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700">Open Ticket Management</button>
                </div>
                {isStaff && <div className="mt-6 rounded-xl border border-indigo-100 bg-indigo-50 p-5"><h3 className="font-bold text-indigo-950">Multi-Agent AI Support System</h3><p className="mt-2 text-sm text-indigo-800">Classification · Hybrid RAG · Troubleshooting · Response Generation · Human Approval · Mirage Vision Evidence</p></div>}
              </>
             )}
          </div>
        </main>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between"><p className="text-sm font-medium text-slate-500">{title}</p><div className="rounded-lg bg-indigo-50 p-2 text-indigo-600"><Icon size={19} /></div></div><p className="mt-5 text-3xl font-bold">{value}</p></div>;
}

export default App;
