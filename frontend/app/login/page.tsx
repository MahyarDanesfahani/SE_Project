"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function LoginPage() {
  const router = useRouter();
  const [registerMode, setRegisterMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError("");
    try {
      const response = await fetch(`${API}/auth/${registerMode ? "register" : "login"}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "ورود انجام نشد");
      localStorage.setItem("zu_access_token", body.access_token);
      router.push("/dashboard");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "خطای ناشناخته"); }
    finally { setLoading(false); }
  }
  return <main className="auth-shell"><div className="auth-card"><span className="eyebrow">ZU ASSISTANT</span><h1>{registerMode ? "ساخت حساب" : "ورود به سامانه"}</h1><form onSubmit={submit}><label>ایمیل<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>رمز عبور<input type="password" minLength={registerMode ? 8 : 1} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error && <div className="form-error">{error}</div>}<button className="primary-button" disabled={loading}>{loading ? "در حال بررسی..." : registerMode ? "ثبت‌نام" : "ورود"}</button></form><button className="link-button" onClick={() => setRegisterMode(!registerMode)}>{registerMode ? "قبلاً حساب ساخته‌ام" : "حساب ندارم؛ ثبت‌نام می‌کنم"}</button></div></main>;
}
