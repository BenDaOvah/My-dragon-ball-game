"use client";

import { useState } from "react";
import DragonArena from "@/components/dragon-arena";

/* ------------------------------------------------------------------ */
/* Palette (kept in sync with the game component)                     */
/* ------------------------------------------------------------------ */
const C = {
  bg0: "#05060f",
  panel: "rgba(20,24,40,0.7)",
  border: "#3a5a8a",
  accent: "#00e5ff",
  orange: "#ff8c2a",
  yellow: "#f9f871",
  green: "#39ff14",
  pink: "#ff2d95",
  purple: "#b14dff",
  red: "#ff3b3b",
  text: "#e6eaf2",
  muted: "#8a94a8",
};

const CONTROLS: { key: string; action: string; note: string; color: string }[] = [
  { key: "A / D",     action: "Walk",        note: "Ground movement",            color: C.accent },
  { key: "W",         action: "Fly / Jump",  note: "Ascend (small Ki cost)",     color: C.accent },
  { key: "S",         action: "Descend",     note: "Drop down while airborne",   color: C.accent },
  { key: "Shift+dir", action: "Dragon Dash", note: "Fast reposition, Ki cost",   color: C.orange },
  { key: "P",         action: "Rush Chain",  note: "Tap up to 4× combo finisher", color: C.pink },
  { key: "I",         action: "Smash",      note: "Charge + release, knockback", color: C.orange },
  { key: "J",         action: "Ki Blast",    note: "Ranged, 14 Ki",              color: C.yellow },
  { key: "K (hold)",  action: "Ki Charge",   note: "Refill Ki; leaves you open", color: C.accent },
  { key: "O (hold)",  action: "Guard",        note: "Reduces damage, drains stamina", color: C.green },
  { key: "E",         action: "Counter",          note: "Free Sonic Sway preemptive OR Revenge burst when hit (1 Skill)", color: C.purple },
  { key: "L",         action: "Transform",    note: "Costs 1 Skill Count; Ki upkeep", color: C.purple },
  { key: "Enter",     action: "Sparking! Mode", note: "Needs full gauge + 1 Skill; free Ki + Ultimate", color: C.yellow },
  { key: "U",         action: "Ultimate Blast", note: "Only in Sparking! Mode",  color: C.yellow },
];

const MECHANICS: { blueprint: string; demo: string; color: string }[] = [
  { blueprint: "Ch.3.1 — Movement is the backbone",
    demo: "Walk/dash/fly form the spacing game; combos are short (4-hit Rush), not the ceiling.",
    color: C.accent },
  { blueprint: "Ch.3.2 — Ki is the universal economy",
    demo: "One Ki bar gates Blast, Dragon Dash, flight, transform upkeep. K holds to charge.",
    color: C.yellow },
  { blueprint: "Ch.3.3 — Layered counters, different costs",
    demo: "Guard (free), Super Perception (timed/free vs melee, 2 Skill vs blasts). Watch the purple ring window.",
    color: C.purple },
  { blueprint: "Ch.3.4 — Sparking! Mode is the shared climax",
    demo: "Fill the orange gauge + spend 1 Skill → 10s of free Ki, then land Ultimate Blast (U).",
    color: C.orange },
  { blueprint: "Ch.5.2 — Log-scaled combat-ratio damage",
    demo: "Goku 416 vs Vegeta 18,000 is a 43× gap, but the log formula keeps it a real fight, not a one-shot.",
    color: C.green },
  { blueprint: "Ch.7 — Mid-battle transformation",
    demo: "L costs 1 Skill Count and adds Ki-upkeep; revert to Base when Ki hits 0 (Noea mastery-lite).",
    color: C.pink },
  { blueprint: "Ch.6.4 — Power Release as throttle",
    demo: "K-charge mirrors Power Release: a fully-released PL only happens when you commit to charging.",
    color: C.accent },
];

export default function Home() {
  const [showControls, setShowControls] = useState(true);

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: C.bg0, color: C.text }}
    >
      {/* CRT scanline overlay */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 z-[60] opacity-30"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to bottom, rgba(255,255,255,0.035) 0px, rgba(255,255,255,0.035) 1px, transparent 1px, transparent 3px)",
          mixBlendMode: "overlay",
        }}
      />

      {/* ===== Header ===== */}
      <header
        className="sticky top-0 z-50 backdrop-blur"
        style={{
          backgroundColor: "rgba(5,6,15,0.78)",
          borderBottom: `1px solid ${C.accent}33`,
          boxShadow: `0 0 18px ${C.accent}1a`,
        }}
      >
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span
              className="inline-flex h-9 w-9 items-center justify-center rounded-md text-lg"
              style={{
                border: `1px solid ${C.orange}`,
                boxShadow: `0 0 12px ${C.orange}88`,
                color: C.orange,
              }}
            >
              ▶
            </span>
            <div>
              <div
                className="text-[13px] sm:text-[15px] font-mono font-bold tracking-wider"
                style={{ color: C.accent, textShadow: `0 0 8px ${C.accent}aa` }}
              >
                DRAGON ARENA
              </div>
              <div className="text-[9px] font-mono" style={{ color: C.muted }}>
                Sparking! ZERO-style combat · canon power levels · Noea-style progression
              </div>
            </div>
          </div>
          <a
            href="/Dragon_Ball_Game_Design_Blueprint.pdf"
            target="_blank"
            rel="noreferrer"
            className="text-[10px] sm:text-[11px] font-mono px-3 py-2 rounded-md transition-colors"
            style={{
              border: `1px solid ${C.yellow}`,
              color: C.yellow,
              boxShadow: `0 0 10px ${C.yellow}33`,
            }}
          >
            📄 DESIGN BLUEPRINT PDF
          </a>
        </div>
      </header>

      {/* ===== Main ===== */}
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 pt-6 pb-12 flex flex-col gap-8">
        {/* Hero */}
        <section className="text-center">
          <h1
            className="font-mono font-bold text-2xl sm:text-4xl tracking-wide"
            style={{ color: C.orange, textShadow: `0 0 16px ${C.orange}88` }}
          >
            GOKU <span style={{ color: C.muted }}>VS</span> VEGETA
          </h1>
          <p className="mt-2 text-[11px] sm:text-sm font-mono" style={{ color: C.muted }}>
            A playable demo of the design blueprint — canon power-level combat-ratio damage,
            Ki-as-universal-economy, layered counters, and a Sparking! Mode climax.
          </p>
          <div className="mt-3 flex flex-wrap items-center justify-center gap-3 text-[10px] font-mono">
            <Tag color={C.orange} label="GOKU · Base 416 PL" />
            <Tag color={C.green} label="→ Kaio-ken ×4 (1664)" />
            <Tag color={C.yellow} label="→ Super Saiyan ×50 (20,800)" />
            <span style={{ color: C.muted }}>vs</span>
            <Tag color={C.accent} label="VEGETA · Base 18,000 PL" />
            <Tag color={C.yellow} label="→ SSJ ×50 @ 50% HP" />
          </div>
        </section>

        {/* Game */}
        <section>
          <DragonArena />
        </section>

        {/* Quick prompt + toggle */}
        <section className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-[11px] font-mono" style={{ color: C.muted }}>
            ▸ Click the canvas, then use keyboard. Mobile: touch buttons below the arena.
          </p>
          <button
            onClick={() => setShowControls(s => !s)}
            className="text-[10px] font-mono px-3 py-1.5 rounded"
            style={{
              border: `1px solid ${C.border}`,
              color: C.accent,
              background: C.panel,
            }}
          >
            {showControls ? "HIDE REFERENCE PANELS" : "SHOW REFERENCE PANELS"}
          </button>
        </section>

        {showControls && (
          <>
            {/* Controls reference */}
            <section>
              <SectionTitle accent={C.accent}>▸ CONTROLS (Sparking! ZERO-style)</SectionTitle>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 mt-3">
                {CONTROLS.map(c => (
                  <div
                    key={c.key}
                    className="rounded-md px-3 py-2 flex items-center gap-3"
                    style={{
                      background: C.panel,
                      border: `1px solid ${c.color}33`,
                    }}
                  >
                    <span
                      className="font-mono font-bold text-[10px] px-2 py-1 rounded shrink-0 min-w-[68px] text-center"
                      style={{ background: `${c.color}22`, color: c.color, border: `1px solid ${c.color}66` }}
                    >
                      {c.key}
                    </span>
                    <div className="min-w-0">
                      <div className="text-[11px] font-mono font-bold" style={{ color: c.color }}>
                        {c.action}
                      </div>
                      <div className="text-[9px] font-mono" style={{ color: C.muted }}>
                        {c.note}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Mechanics mapping */}
            <section>
              <SectionTitle accent={C.orange}>▸ HOW THE DEMO MAPS TO THE BLUEPRINT</SectionTitle>
              <div className="rounded-lg overflow-hidden mt-3" style={{ border: `1px solid ${C.border}` }}>
                {MECHANICS.map((m, i) => (
                  <div
                    key={i}
                    className="grid grid-cols-1 sm:grid-cols-[1fr_1.4fr] gap-2 px-4 py-3"
                    style={{
                      background: i % 2 === 0 ? "rgba(20,24,40,0.6)" : "rgba(13,17,32,0.6)",
                      borderBottom: i < MECHANICS.length - 1 ? `1px solid ${C.border}33` : "none",
                    }}
                  >
                    <div className="text-[11px] font-mono font-bold" style={{ color: m.color }}>
                      {m.blueprint}
                    </div>
                    <div className="text-[11px] font-mono" style={{ color: C.text }}>
                      {m.demo}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Combat math explainer */}
            <section>
              <SectionTitle accent={C.green}>▸ THE DAMAGE FORMULA (Chapter 5)</SectionTitle>
              <div
                className="rounded-lg px-4 py-4 mt-3 font-mono text-[11px] leading-relaxed"
                style={{
                  background: "rgba(10,14,26,0.9)",
                  border: `1px solid ${C.green}44`,
                  color: C.green,
                }}
              >
                <div>ratio      = attacker.PL / max(defender.PL, 1)</div>
                <div>ratioScale = log10(ratio + 9)</div>
                <div>finalDamage = move.baseDamage × ratioScale</div>
                <div className="mt-3" style={{ color: C.muted }}>
                  ▸ Goku Base (416) vs Vegeta (18,000): ratio 0.023 → ratioScale 0.955 → ~full base damage (the floor)
                </div>
                <div style={{ color: C.muted }}>
                  ▸ Goku SSJ (20,800) vs Vegeta (18,000): ratio 1.16 → ratioScale 1.007 → near-even, slight edge
                </div>
                <div style={{ color: C.muted }}>
                  ▸ The 43× canon power gap is a 1.0–1.3× damage swing — a real fight, not a one-shot. That is the whole point of the log formula.
                </div>
              </div>
            </section>
          </>
        )}

        {/* Footer note */}
        <section>
          <p className="text-[10px] font-mono text-center" style={{ color: C.muted }}>
            Demo built from the Dragon Ball Game Design &amp; Engineering Blueprint. All combat
            mechanics trace to a chapter of the PDF. Canon power levels sourced to the manga
            (ch.215+), Daizenshuu 7, and V-Jump.
          </p>
        </section>
      </main>

      {/* ===== Footer (sticky to bottom) ===== */}
      <footer
        className="mt-auto"
        style={{
          borderTop: `1px solid ${C.orange}33`,
          boxShadow: `0 0 18px ${C.orange}1a`,
          backgroundColor: "rgba(5,6,15,0.6)",
        }}
      >
        <div className="mx-auto max-w-6xl px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-[10px] font-mono" style={{ color: C.muted }}>
            DRAGON ARENA · BUILT FROM THE DESIGN BLUEPRINT
          </p>
          <p className="text-[10px] font-mono" style={{ color: C.muted }}>
            Original engines · canon-accurate power levels · no trademarked assets
          </p>
        </div>
      </footer>
    </div>
  );
}

function Tag({ color, label }: { color: string; label: string }) {
  return (
    <span
      className="font-mono font-bold px-2 py-1 rounded"
      style={{ background: `${color}1a`, color, border: `1px solid ${color}44` }}
    >
      {label}
    </span>
  );
}

function SectionTitle({ children, accent }: { children: React.ReactNode; accent: string }) {
  return (
    <h2
      className="font-mono font-bold text-[13px] sm:text-[14px] tracking-wider"
      style={{ color: accent, textShadow: `0 0 8px ${accent}66` }}
    >
      {children}
    </h2>
  );
}
