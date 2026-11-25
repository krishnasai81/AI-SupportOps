import { useState } from "react";
import { Headset, Loader2, ShieldCheck, UserRound } from "lucide-react";
import { login, registerCustomer } from "../services/api";

export default function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const user = mode === "register"
        ? await registerCustomer({ name, email, password })
        : await login({ email, password });
      onAuthenticated(user);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-7 flex items-center gap-3">
          <div className="rounded-xl bg-indigo-600 p-3 text-white"><Headset size={24} /></div>
          <div><h1 className="text-xl font-bold">AI SupportOps</h1><p className="text-sm text-slate-500">Customer support workspace</p></div>
        </div>
        <div className="mb-6 flex rounded-lg bg-slate-100 p-1">
          <button onClick={() => setMode("login")} className={`flex-1 rounded-md py-2 text-sm font-semibold ${mode === "login" ? "bg-white shadow-sm" : "text-slate-500"}`}>Sign in</button>
          <button onClick={() => setMode("register")} className={`flex-1 rounded-md py-2 text-sm font-semibold ${mode === "register" ? "bg-white shadow-sm" : "text-slate-500"}`}>Create customer account</button>
        </div>
        <form onSubmit={submit} className="space-y-4">
          {mode === "register" && <label className="block text-sm font-medium">Full name<input required minLength={2} value={name} onChange={e => setName(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3" autoComplete="name" /></label>}
          <label className="block text-sm font-medium">Email<input required type="email" value={email} onChange={e => setEmail(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3" autoComplete="email" /></label>
          <label className="block text-sm font-medium">Password<input required minLength={mode === "register" ? 10 : 1} type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3" autoComplete={mode === "register" ? "new-password" : "current-password"} /></label>
          {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white disabled:opacity-60">
            {busy ? <Loader2 size={17} className="animate-spin" /> : mode === "register" ? <UserRound size={17} /> : <ShieldCheck size={17} />}
            {busy ? "Please wait..." : mode === "register" ? "Create account" : "Sign in"}
          </button>
        </form>
        <p className="mt-5 text-xs leading-5 text-slate-500">
          Customer accounts can be created here. Support-team accounts are provisioned by an administrator.
        </p>
      </div>
    </div>
  );
}
