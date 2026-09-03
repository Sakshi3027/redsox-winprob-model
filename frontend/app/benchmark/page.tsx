import BenchmarkClient from "./BenchmarkClient";

async function getBenchmark() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_BASE}/benchmark`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch benchmark");
  return res.json();
}

export default async function BenchmarkPage() {
  const benchmark = await getBenchmark();
  return <BenchmarkClient benchmark={benchmark} />;
}
