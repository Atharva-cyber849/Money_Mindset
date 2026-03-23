import { useState, useEffect, useRef } from "react";

const FONTS = `@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Clash+Display:wght@400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');`;

// ── MOCK DATA ──────────────────────────────────────────────────────────────
const STOCKS = [
  { sym: "NIFTY 50", val: "24,762.15", chg: "+1.24%", up: true },
  { sym: "SENSEX", val: "81,559.54", chg: "+1.18%", up: true },
  { sym: "RELIANCE", val: "₹2,941.30", chg: "-0.43%", up: false },
  { sym: "TCS", val: "₹4,123.85", chg: "+0.87%", up: true },
  { sym: "HDFC BANK", val: "₹1,812.45", chg: "+2.11%", up: true },
  { sym: "INFOSYS", val: "₹1,934.60", chg: "-0.29%", up: false },
  { sym: "WIPRO", val: "₹578.90", chg: "+0.64%", up: true },
  { sym: "BAJAJ FIN", val: "₹7,234.10", chg: "-1.02%", up: false },
  { sym: "GOLD", val: "₹73,240", chg: "+0.31%", up: true },
  { sym: "USD/INR", val: "83.47", chg: "+0.12%", up: false },
];

const NEWS = [
  { tag: "RBI POLICY", title: "RBI holds repo rate at 6.5% for sixth consecutive meeting", time: "2h ago", impact: "Your FDs and EMIs remain unchanged.", color: "#00d4b8" },
  { tag: "BUDGET", title: "FM hints at capital gains tax revision in upcoming Budget 2026", time: "4h ago", impact: "May affect your ELSS and equity returns.", color: "#f59e0b" },
  { tag: "MARKETS", title: "Nifty 50 crosses 24,700 — FII buying resumes after 3-week selloff", time: "6h ago", impact: "Good time to review your SIP strategy.", color: "#4ade80" },
  { tag: "CRYPTO", title: "India's 30% crypto tax regime under review by parliamentary panel", time: "8h ago", impact: "Hold off large crypto moves till clarity.", color: "#a78bfa" },
  { tag: "SEBI", title: "SEBI mandates T+0 settlement for top 500 stocks from April 2026", time: "1d ago", impact: "Faster liquidity for your equity trades.", color: "#00d4b8" },
];

const UPCOMING = [
  { date: "MAR 28", label: "RBI MPC Minutes", type: "event", icon: "🏦" },
  { date: "MAR 31", label: "FY25 Tax Filing Deadline", type: "deadline", icon: "🧾" },
  { date: "APR 01", label: "New Tax Year Begins", type: "milestone", icon: "📅" },
  { date: "APR 15", label: "Q4 Results: TCS, Infosys", type: "market", icon: "📊" },
  { date: "APR 22", label: "Weekly Challenge Resets", type: "game", icon: "🏆" },
  { date: "MAY 01", label: "Budget Session Opens", type: "event", icon: "🏛️" },
];

const MODULES = [
  { icon: "📉", label: "Market Replay", tag: "3 events", color: "#00d4b8", locked: false },
  { icon: "🎯", label: "Scenarios", tag: "4 new", color: "#f59e0b", locked: false },
  { icon: "🫙", label: "Gullak", tag: "Level 2", color: "#4ade80", locked: false },
  { icon: "🌊", label: "Black Swan", tag: "Unlock at 50 IQ", color: "#a78bfa", locked: true },
  { icon: "📈", label: "Dalal Street", tag: "Unlock at 70 IQ", color: "#f87171", locked: true },
  { icon: "🏙️", label: "Karobaar", tag: "Unlock at 85 IQ", color: "#fb923c", locked: true },
];

const ACHIEVEMENTS = [
  { icon: "🔥", label: "7-Day Streak", earned: true },
  { icon: "💡", label: "First Scenario", earned: true },
  { icon: "📊", label: "Market Survivor", earned: true },
  { icon: "🏆", label: "Top 100", earned: false },
  { icon: "🧠", label: "IQ 75+", earned: false },
];

const MINI_CHART = [42, 38, 55, 48, 62, 58, 71, 65, 78, 74, 82, 79];

// ── SPARKLINE ─────────────────────────────────────────────────────────────
function Spark({ data, color = "#00d4b8", h = 36 }) {
  const w = 80;
  const min = Math.min(...data), max = Math.max(...data);
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / (max - min)) * (h - 4) - 2;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <polyline points={`0,${h} ${pts} ${w},${h}`} fill={color} fillOpacity="0.08" stroke="none" />
    </svg>
  );
}

// ── IQ RING ────────────────────────────────────────────────────────────────
function IQRing({ score = 63, size = 110 }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    <svg width={size} height={size} style={{ display: "block" }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(0,212,184,0.1)" strokeWidth="8" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#00d4b8" strokeWidth="8"
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round" transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)" }} />
      <text x={size / 2} y={size / 2 - 5} textAnchor="middle" fill="#e8f4f0"
        style={{ fontFamily: "'DM Mono', monospace", fontSize: 22, fontWeight: 500 }}>{score}</text>
      <text x={size / 2} y={size / 2 + 14} textAnchor="middle" fill="#4a7a72"
        style={{ fontFamily: "'DM Mono', monospace", fontSize: 10 }}>FINANCE IQ</text>
    </svg>
  );
}

// ── XP BAR ─────────────────────────────────────────────────────────────────
function XPBar({ current = 1250, max = 2000 }) {
  const pct = (current / max) * 100;
  return (
    <div style={{ width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#4a7a72" }}>LEVEL 2</span>
        <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#f59e0b" }}>{current.toLocaleString()} / {max.toLocaleString()} XP</span>
      </div>
      <div style={{ height: 6, background: "rgba(255,255,255,0.06)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: "linear-gradient(90deg, #f59e0b, #fbbf24)", borderRadius: 3, transition: "width 1s ease" }} />
      </div>
      <div style={{ textAlign: "right", marginTop: 5 }}>
        <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#4a7a72" }}>750 XP to Level 3</span>
      </div>
    </div>
  );
}

// ── TICKER ─────────────────────────────────────────────────────────────────
function Ticker() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let pos = 0;
    const speed = 0.5;
    const loop = () => {
      pos -= speed;
      if (pos <= -el.scrollWidth / 2) pos = 0;
      el.style.transform = `translateX(${pos}px)`;
      requestAnimationFrame(loop);
    };
    const id = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(id);
  }, []);
  const items = [...STOCKS, ...STOCKS];
  return (
    <div style={{ overflow: "hidden", background: "rgba(0,0,0,0.3)", borderBottom: "1px solid rgba(0,212,184,0.1)", padding: "8px 0" }}>
      <div ref={ref} style={{ display: "flex", gap: 0, width: "max-content", willChange: "transform" }}>
        {items.map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "0 28px", borderRight: "1px solid rgba(255,255,255,0.05)" }}>
            <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#4a7a72", letterSpacing: "0.06em" }}>{s.sym}</span>
            <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#e8f4f0", fontWeight: 500 }}>{s.val}</span>
            <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: s.up ? "#4ade80" : "#f87171" }}>{s.up ? "▲" : "▼"} {s.chg}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── MAIN DASHBOARD ─────────────────────────────────────────────────────────
export default function Dashboard() {
  const [activeNews, setActiveNews] = useState(0);
  const [time, setTime] = useState(new Date());
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const fmt = (d) => d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const fmtDate = (d) => d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" });

  return (
    <>
      <style>{FONTS}{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #080c0b; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0,212,184,0.2); border-radius: 2px; }

        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.5; }
        }
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 20px rgba(0,212,184,0.15); }
          50%       { box-shadow: 0 0 40px rgba(0,212,184,0.3); }
        }
        @keyframes scanline {
          0%   { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }

        .card {
          background: rgba(255,255,255,0.025);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 14px;
          backdrop-filter: blur(8px);
          transition: border-color 0.25s, box-shadow 0.25s;
        }
        .card:hover { border-color: rgba(0,212,184,0.2); }
        .card-teal { border-color: rgba(0,212,184,0.15); animation: glow 4s ease-in-out infinite; }

        .nav-item {
          display: flex; align-items: center; gap: 10px;
          padding: 10px 14px; border-radius: 10px;
          cursor: pointer; transition: all 0.2s;
          color: #4a7a72; font-family: 'DM Sans', sans-serif; font-size: 13px;
          border: 1px solid transparent;
        }
        .nav-item:hover { background: rgba(255,255,255,0.04); color: #a0c4bc; }
        .nav-item.active { background: rgba(0,212,184,0.08); color: #00d4b8; border-color: rgba(0,212,184,0.2); }

        .module-card {
          background: rgba(255,255,255,0.025);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 12px; padding: 14px;
          cursor: pointer; transition: all 0.22s;
          position: relative; overflow: hidden;
        }
        .module-card:not(.locked):hover {
          transform: translateY(-2px);
          border-color: rgba(0,212,184,0.3);
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .module-card.locked { opacity: 0.45; cursor: not-allowed; }

        .news-item {
          padding: 14px 16px; border-radius: 10px;
          cursor: pointer; transition: all 0.2s;
          border: 1px solid transparent;
        }
        .news-item:hover, .news-item.active {
          background: rgba(255,255,255,0.04);
          border-color: rgba(255,255,255,0.08);
        }

        .upcoming-row {
          display: flex; align-items: center; gap: 12px;
          padding: 10px 14px; border-radius: 10px;
          transition: background 0.2s; cursor: pointer;
        }
        .upcoming-row:hover { background: rgba(255,255,255,0.04); }

        .btn-primary {
          background: #00d4b8; color: #080c0b;
          border: none; border-radius: 8px;
          font-family: 'Clash Display', sans-serif;
          font-weight: 600; font-size: 13px;
          padding: 9px 20px; cursor: pointer;
          transition: all 0.2s; letter-spacing: 0.02em;
        }
        .btn-primary:hover { background: #00ead0; transform: translateY(-1px); }

        .btn-ghost {
          background: transparent; color: #4a7a72;
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 8px; font-family: 'DM Sans', sans-serif;
          font-size: 12px; padding: 7px 14px; cursor: pointer;
          transition: all 0.2s;
        }
        .btn-ghost:hover { color: #00d4b8; border-color: rgba(0,212,184,0.3); }

        .tag {
          display: inline-flex; align-items: center;
          padding: 3px 8px; border-radius: 20px;
          font-family: 'DM Mono', monospace; font-size: 9px;
          font-weight: 500; letter-spacing: 0.08em;
        }

        .anim-0 { animation: fadeSlideUp 0.5s 0.05s both; }
        .anim-1 { animation: fadeSlideUp 0.5s 0.1s both; }
        .anim-2 { animation: fadeSlideUp 0.5s 0.15s both; }
        .anim-3 { animation: fadeSlideUp 0.5s 0.2s both; }
        .anim-4 { animation: fadeSlideUp 0.5s 0.25s both; }
        .anim-5 { animation: fadeSlideUp 0.5s 0.3s both; }
      `}</style>

      <div style={{ minHeight: "100vh", background: "#080c0b", fontFamily: "'DM Sans', sans-serif", position: "relative" }}>

        {/* subtle grid overlay */}
        <div style={{ position: "fixed", inset: 0, backgroundImage: "linear-gradient(rgba(0,212,184,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,184,0.015) 1px, transparent 1px)", backgroundSize: "48px 48px", pointerEvents: "none", zIndex: 0 }} />

        {/* ── SIDEBAR ── */}
        <div style={{ position: "fixed", left: 0, top: 0, bottom: 0, width: 220, background: "rgba(8,12,11,0.95)", borderRight: "1px solid rgba(255,255,255,0.06)", zIndex: 50, display: "flex", flexDirection: "column", padding: "20px 12px" }}>

          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 6px", marginBottom: 32 }}>
            <div style={{ width: 34, height: 34, background: "linear-gradient(135deg, #00d4b8, #006b5e)", borderRadius: 9, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 17, flexShrink: 0 }}>💰</div>
            <div>
              <div style={{ fontFamily: "'Clash Display', sans-serif", fontWeight: 700, fontSize: 15, color: "#e8f4f0", lineHeight: 1 }}>Money Mindset</div>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#2a5a52", letterSpacing: "0.1em", marginTop: 3 }}>BETA · v0.9.2</div>
            </div>
          </div>

          {/* Nav */}
          <div style={{ display: "flex", flexDirection: "column", gap: 3, flex: 1 }}>
            {[
              { icon: "⊞", label: "Dashboard", active: true },
              { icon: "◉", label: "Personality" },
              { icon: "⟳", label: "Simulations" },
              { icon: "◈", label: "Games" },
              { icon: "↗", label: "Analytics" },
              { icon: "▤", label: "My Progress" },
              { icon: "◎", label: "Goals" },
              { icon: "◌", label: "AI Tutor" },
              { icon: "✦", label: "Achievements" },
              { icon: "◻", label: "Learn" },
            ].map(n => (
              <div key={n.label} className={`nav-item ${n.active ? "active" : ""}`}>
                <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 14, width: 18, textAlign: "center" }}>{n.icon}</span>
                <span>{n.label}</span>
                {n.active && <div style={{ marginLeft: "auto", width: 5, height: 5, borderRadius: "50%", background: "#00d4b8" }} />}
              </div>
            ))}
          </div>

          {/* User card */}
          <div style={{ padding: "12px 10px", background: "rgba(0,212,184,0.06)", border: "1px solid rgba(0,212,184,0.12)", borderRadius: 12, marginTop: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 34, height: 34, borderRadius: "50%", background: "linear-gradient(135deg, #00d4b8, #006b5e)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Clash Display',sans-serif", fontWeight: 700, fontSize: 13, color: "#080c0b" }}>AT</div>
              <div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500, color: "#e8f4f0" }}>Atharva</div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#4a7a72" }}>THE BUILDER · LVL 2</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── MAIN CONTENT ── */}
        <div style={{ marginLeft: 220, position: "relative", zIndex: 1 }}>

          {/* ── TOPBAR ── */}
          <div style={{ position: "sticky", top: 0, zIndex: 40, background: "rgba(8,12,11,0.92)", backdropFilter: "blur(12px)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 28px" }}>
              <div>
                <div style={{ fontFamily: "'Clash Display', sans-serif", fontSize: 20, fontWeight: 700, color: "#e8f4f0" }}>Good morning, Atharva 👋</div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#4a7a72", marginTop: 2 }}>{fmtDate(time)} · {fmt(time)} IST · Markets open</div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.25)", borderRadius: 20, padding: "5px 12px" }}>
                  <span style={{ fontSize: 13 }}>🔥</span>
                  <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#f59e0b", fontWeight: 500 }}>7 day streak</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(0,212,184,0.08)", border: "1px solid rgba(0,212,184,0.2)", borderRadius: 20, padding: "5px 12px" }}>
                  <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#00d4b8" }}>⚡ 1,250 XP</span>
                </div>
                <div style={{ width: 36, height: 36, borderRadius: "50%", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: 15 }}>🔔</div>
              </div>
            </div>
            <Ticker />
          </div>

          {/* ── DASHBOARD GRID ── */}
          <div style={{ padding: "24px 28px", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gridTemplateRows: "auto", gap: 16 }}>

            {/* ── ROW 1: HERO STATS ── */}

            {/* Finance IQ + XP card */}
            <div className="card card-teal anim-0" style={{ padding: "22px 24px", gridColumn: "1", display: "flex", gap: 20, alignItems: "center" }}>
              <IQRing score={63} />
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em", marginBottom: 4 }}>YOUR PROGRESS</div>
                <div style={{ fontFamily: "'Clash Display', sans-serif", fontSize: 22, fontWeight: 700, color: "#e8f4f0", marginBottom: 2 }}>Level 2</div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: "#4a7a72", marginBottom: 14 }}>The Careful Builder</div>
                <XPBar />
              </div>
            </div>

            {/* Market pulse */}
            <div className="card anim-1" style={{ padding: "20px 22px", gridColumn: "2" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                <div>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em", marginBottom: 4 }}>MARKET PULSE</div>
                  <div style={{ fontFamily: "'Clash Display', sans-serif", fontSize: 18, fontWeight: 700, color: "#e8f4f0" }}>NIFTY 50</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 20, fontWeight: 500, color: "#e8f4f0" }}>24,762</div>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#4ade80" }}>▲ +1.24%</div>
                </div>
              </div>
              <Spark data={MINI_CHART} color="#4ade80" h={48} />
              <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
                {[["SENSEX", "81,559", "+1.18%", true], ["GOLD", "₹73,240", "+0.31%", true], ["INR", "83.47", "+0.12%", false]].map(([s, v, c, u]) => (
                  <div key={s} style={{ flex: 1, background: "rgba(255,255,255,0.03)", borderRadius: 8, padding: "8px 10px" }}>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#4a7a72", marginBottom: 3 }}>{s}</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#e8f4f0", fontWeight: 500 }}>{v}</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: u ? "#4ade80" : "#f87171" }}>{u ? "▲" : "▼"} {c}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Daily challenge */}
            <div className="card anim-2" style={{ padding: "20px 22px", gridColumn: "3", background: "linear-gradient(135deg, rgba(245,158,11,0.08), rgba(245,158,11,0.03))", borderColor: "rgba(245,158,11,0.2)" }}>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#f59e0b", letterSpacing: "0.1em", marginBottom: 12 }}>TODAY'S CHALLENGE</div>
              <div style={{ fontFamily: "'Clash Display', sans-serif", fontSize: 17, fontWeight: 700, color: "#e8f4f0", marginBottom: 8, lineHeight: 1.35 }}>Survive the 2008 Sensex crash with ₹50,000</div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: "#8a9e9a", marginBottom: 16, lineHeight: 1.6 }}>Can you hold through a 60% crash and come out ahead? 14,203 users have tried this week.</div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                <div style={{ display: "flex", gap: 8 }}>
                  <span className="tag" style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b" }}>+200 XP</span>
                  <span className="tag" style={{ background: "rgba(74,222,128,0.1)", color: "#4ade80" }}>HARD</span>
                </div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72" }}>Ends in 14h 22m</div>
              </div>
              <button className="btn-primary" style={{ width: "100%" }}>Start Challenge →</button>
            </div>

            {/* ── ROW 2: NEWS + MODULES ── */}

            {/* Financial news */}
            <div className="card anim-3" style={{ padding: "20px 0", gridColumn: "1 / 3", gridRow: "2" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0 20px", marginBottom: 12 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em" }}>FINANCIAL NEWS · INDIA</div>
                <button className="btn-ghost">View all →</button>
              </div>

              {/* Active news detail */}
              {activeNews !== null && (
                <div style={{ margin: "0 16px 12px", background: "rgba(255,255,255,0.03)", border: `1px solid ${NEWS[activeNews].color}30`, borderLeft: `3px solid ${NEWS[activeNews].color}`, borderRadius: "0 10px 10px 0", padding: "14px 16px" }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6 }}>
                    <span className="tag" style={{ background: `${NEWS[activeNews].color}20`, color: NEWS[activeNews].color }}>{NEWS[activeNews].tag}</span>
                    <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72" }}>{NEWS[activeNews].time}</span>
                  </div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: "#e8f4f0", marginBottom: 8, lineHeight: 1.5 }}>{NEWS[activeNews].title}</div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: "#4ade80" }}>💡 {NEWS[activeNews].impact}</div>
                </div>
              )}

              <div style={{ display: "flex", flexDirection: "column" }}>
                {NEWS.map((n, i) => (
                  <div key={i} className={`news-item ${activeNews === i ? "active" : ""}`}
                    onClick={() => setActiveNews(i)}
                    style={{ padding: "10px 20px", borderLeft: `2px solid ${activeNews === i ? n.color : "transparent"}`, marginLeft: 0 }}>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <span className="tag" style={{ background: `${n.color}15`, color: n.color, flexShrink: 0 }}>{n.tag}</span>
                      <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: activeNews === i ? "#e8f4f0" : "#8a9e9a", lineHeight: 1.4, flex: 1 }}>{n.title}</span>
                      <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#2a5a52", flexShrink: 0 }}>{n.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming events */}
            <div className="card anim-4" style={{ padding: "20px 0", gridColumn: "3", gridRow: "2" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0 20px", marginBottom: 14 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em" }}>UPCOMING</div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", animation: "pulse 2s infinite" }}>● LIVE</div>
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                {UPCOMING.map((u, i) => {
                  const typeColor = { event: "#00d4b8", deadline: "#f87171", milestone: "#a78bfa", market: "#f59e0b", game: "#4ade80" }[u.type];
                  return (
                    <div key={i} className="upcoming-row" style={{ margin: "0 8px" }}>
                      <div style={{ width: 44, flexShrink: 0, textAlign: "center" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: typeColor, fontWeight: 500 }}>{u.date}</div>
                      </div>
                      <div style={{ width: 28, height: 28, borderRadius: 7, background: `${typeColor}15`, border: `1px solid ${typeColor}25`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, flexShrink: 0 }}>{u.icon}</div>
                      <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: "#8a9e9a", flex: 1, lineHeight: 1.4 }}>{u.label}</div>
                      <div style={{ width: 6, height: 6, borderRadius: "50%", background: typeColor, flexShrink: 0, opacity: 0.6 }} />
                    </div>
                  );
                })}
              </div>
              <div style={{ margin: "14px 12px 0", padding: "10px 14px", background: "rgba(167,139,250,0.08)", border: "1px solid rgba(167,139,250,0.2)", borderRadius: 10 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#a78bfa", marginBottom: 4 }}>REMINDER</div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: "#8a9e9a", lineHeight: 1.5 }}>FY25 tax filing deadline in <span style={{ color: "#f87171", fontWeight: 500 }}>3 days</span>. Check your 80C investments.</div>
              </div>
            </div>

            {/* ── ROW 3: MODULES + ACHIEVEMENTS + SIP ── */}

            {/* Game modules */}
            <div className="card anim-5" style={{ padding: "20px 22px", gridColumn: "1 / 3", gridRow: "3" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em" }}>SIMULATION MODULES</div>
                <span className="tag" style={{ background: "rgba(0,212,184,0.1)", color: "#00d4b8" }}>3 UNLOCKED · 3 LOCKED</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 10 }}>
                {MODULES.map((m, i) => (
                  <div key={i} className={`module-card ${m.locked ? "locked" : ""}`}>
                    {m.locked && (
                      <div style={{ position: "absolute", top: 8, right: 8, fontSize: 10 }}>🔒</div>
                    )}
                    <div style={{ fontSize: 22, marginBottom: 8 }}>{m.icon}</div>
                    <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, fontWeight: 500, color: "#e8f4f0", marginBottom: 4 }}>{m.label}</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: m.locked ? "#4a7a72" : m.color }}>{m.tag}</div>
                    {!m.locked && <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 2, background: m.color, borderRadius: "0 0 12px 12px", opacity: 0.6 }} />}
                  </div>
                ))}
              </div>
            </div>

            {/* Right column: achievements + SIP tracker */}
            <div style={{ gridColumn: "3", gridRow: "3", display: "flex", flexDirection: "column", gap: 14 }}>

              {/* Achievements */}
              <div className="card" style={{ padding: "18px 20px", flex: 1 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em", marginBottom: 14 }}>ACHIEVEMENTS</div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {ACHIEVEMENTS.map((a, i) => (
                    <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 5, opacity: a.earned ? 1 : 0.3 }}>
                      <div style={{ width: 40, height: 40, borderRadius: 10, background: a.earned ? "rgba(245,158,11,0.12)" : "rgba(255,255,255,0.04)", border: `1px solid ${a.earned ? "rgba(245,158,11,0.3)" : "rgba(255,255,255,0.06)"}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>{a.icon}</div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 8, color: a.earned ? "#f59e0b" : "#4a7a72", textAlign: "center", lineHeight: 1.3, maxWidth: 42 }}>{a.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* SIP tracker */}
              <div className="card" style={{ padding: "18px 20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em" }}>SIP TRACKER</div>
                  <span className="tag" style={{ background: "rgba(74,222,128,0.1)", color: "#4ade80" }}>ACTIVE</span>
                </div>
                {[["Nifty 50 Index", "₹2,000/mo", "+14.3%"], ["ELSS (80C)", "₹1,500/mo", "+11.8%"]].map(([name, amt, ret]) => (
                  <div key={name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                    <div>
                      <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: "#e8f4f0" }}>{name}</div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72" }}>{amt}</div>
                    </div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#4ade80" }}>{ret}</div>
                  </div>
                ))}
                <div style={{ marginTop: 10, display: "flex", justifyContent: "space-between" }}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72" }}>Total invested</div>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#e8f4f0", fontWeight: 500 }}>₹42,000</div>
                </div>
              </div>
            </div>

            {/* ── ROW 4: AI TUTOR QUICK ASK + LEADERBOARD ── */}

            {/* AI Tutor quick ask */}
            <div className="card anim-5" style={{ padding: "20px 22px", gridColumn: "1 / 3", gridRow: "4", background: "linear-gradient(135deg, rgba(83,74,183,0.06), rgba(0,212,184,0.04))", borderColor: "rgba(83,74,183,0.2)" }}>
              <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "linear-gradient(135deg, rgba(83,74,183,0.3), rgba(0,212,184,0.2))", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, flexShrink: 0 }}>🤖</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#7F77DD", letterSpacing: "0.1em", marginBottom: 6 }}>AI TUTOR · PERSONALISED TO YOUR PROFILE</div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: "#8a9e9a", marginBottom: 14, lineHeight: 1.6 }}>
                    Based on your profile, your biggest gap is <span style={{ color: "#00d4b8" }}>tax-advantaged investing</span>. You're in the 30% tax bracket but haven't explored NPS or ELSS beyond basic 80C. Want me to explain how to save ₹46,800 more in tax this year?
                  </div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {["Yes, explain NPS for me →", "Show me ELSS options →", "How much tax am I saving? →"].map(q => (
                      <button key={q} className="btn-ghost" style={{ fontSize: 12 }}>{q}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Leaderboard */}
            <div className="card anim-5" style={{ padding: "20px 22px", gridColumn: "3", gridRow: "4" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a7a72", letterSpacing: "0.1em" }}>WEEKLY LEADERBOARD</div>
                <span className="tag" style={{ background: "rgba(74,222,128,0.1)", color: "#4ade80" }}>LIVE</span>
              </div>
              {[
                ["#1", "Priya S.", "Mumbai", 4820],
                ["#2", "Rohit M.", "Pune", 4310],
                ["#3", "Sneha K.", "Bangalore", 3990],
                ["#47", "You", "Mumbai", 1250],
              ].map(([rank, name, city, xp], i) => (
                <div key={i} style={{ display: "flex", gap: 10, alignItems: "center", padding: "8px 10px", borderRadius: 8, background: name === "You" ? "rgba(0,212,184,0.06)" : "transparent", border: name === "You" ? "1px solid rgba(0,212,184,0.15)" : "1px solid transparent", marginBottom: 4 }}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: i < 3 ? "#f59e0b" : "#4a7a72", width: 26, fontWeight: 500 }}>{rank}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: name === "You" ? "#00d4b8" : "#e8f4f0", fontWeight: name === "You" ? 500 : 400 }}>{name}</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#4a7a72" }}>{city}</div>
                  </div>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: name === "You" ? "#00d4b8" : "#8a9e9a" }}>⚡ {xp.toLocaleString()}</div>
                </div>
              ))}
              <button className="btn-ghost" style={{ width: "100%", marginTop: 8 }}>View full leaderboard →</button>
            </div>

          </div>
        </div>
      </div>
    </>
  );
}
