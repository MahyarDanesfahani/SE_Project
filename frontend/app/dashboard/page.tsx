"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Dashboard = { greeting: string; metrics: { value: string; label: string }[]; upcoming: { title: string; starts_at: string | null; type: string }[]; announcements: { title: string; category: string; source_name: string }[] };

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("برای مشاهده داشبورد باید وارد شوید.");
  useEffect(() => { const token = localStorage.getItem("zu_access_token"); if (!token) { router.push("/login"); return; } fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1"}/dashboard`, { headers: { Authorization: `Bearer ${token}` } }).then((response) => { if (response.status === 401) { localStorage.removeItem("zu_access_token"); router.push("/login"); throw new Error(); } if (!response.ok) throw new Error(); return response.json(); }).then(setData).catch(() => setError("داده داشبورد هنوز در دسترس نیست.")); }, [router]);
  return <main className="dashboard"><div className="dashboard-header"><span className="eyebrow">ZU ASSISTANT</span><button className="link-button" onClick={() => { localStorage.removeItem("zu_access_token"); router.push("/login"); }}>خروج</button><h1>{data?.greeting ?? "داشبورد دانشجو"}</h1><p>نمایی یکپارچه از وضعیت آموزشی و کارهای نزدیک شما</p></div>{data ? <><section className="metrics">{data.metrics.map((metric) => <div className="metric" key={metric.label}><strong>{metric.value}</strong><span>{metric.label}</span></div>)}</section><div className="dashboard-grid"><section className="panel"><h2>رویدادهای نزدیک</h2>{data.upcoming.length ? data.upcoming.map((event) => <div className="list-row" key={`${event.type}-${event.title}`}><span>{event.title}</span><small>{event.starts_at ? new Date(event.starts_at).toLocaleString("fa-IR") : "بدون تاریخ"}</small></div>) : <p>رویداد نزدیکی وجود ندارد.</p>}</section><section className="panel"><h2>اطلاعیه‌های اخیر</h2>{data.announcements.length ? data.announcements.map((item) => <div className="list-row" key={item.title}><span>{item.title}</span><small>{item.source_name}</small></div>) : <p>اطلاعیه‌ای وجود ندارد.</p>}</section></div></> : <div className="status-card"><strong>{error}</strong><span>پس از ورود، اطلاعات واقعی حساب شما نمایش داده می‌شود.</span></div>}</main>;
}
