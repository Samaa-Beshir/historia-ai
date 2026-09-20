"use client";

import { useEffect, useRef, useState } from "react";

import { ChatWindow } from "@/components/ChatWindow";
import { EraTimeline } from "@/components/EraTimeline";
import { ThemeToggle } from "@/components/ThemeToggle";
import { getEraTheme } from "@/lib/eras";
import { useChatStore } from "@/store/chatStore";

export function ChatApp() {
  const activeEra = useChatStore((s) => s.activeEra);
  const theme = getEraTheme(activeEra);
  const previousEra = useRef(activeEra);
  const [isTraveling, setIsTraveling] = useState(false);

  useEffect(() => {
    if (previousEra.current === activeEra) return;
    previousEra.current = activeEra;
    setIsTraveling(true);
    const timer = window.setTimeout(() => setIsTraveling(false), 2300);
    return () => window.clearTimeout(timer);
  }, [activeEra]);

  return (
    <div
      className="historia-shell relative isolate flex flex-col flex-1 min-h-0 overflow-hidden"
      style={
        {
          "--accent": theme.accent,
          "--accent-soft": theme.accentSoft,
          "--on-accent": theme.onAccent,
          "--era-glow": theme.glow,
          "--era-surface": theme.surface,
          "--era-background": theme.background,
        } as React.CSSProperties
      }
    >
      <div className="era-atmosphere" aria-hidden="true">
        <div className="era-glow" />
        <div className="era-grid" />
        <div className="era-emblem">{theme.motif}</div>
        <div className="era-horizon" />
      </div>

      {isTraveling && (
        <div className="time-travel-overlay" role="status" aria-live="polite">
          <div className="portal-ring"><span>{theme.motif}</span></div>
          <p className="mt-5 text-xs uppercase tracking-[0.35em] text-white/55">Time travel in progress</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">{theme.arabicLabel}</h2>
          <p className="mt-1 text-sm text-white/60">{theme.label} · {theme.range}</p>
        </div>
      )}

      <header className="relative z-10 flex items-center justify-between gap-4 border-b border-white/10 bg-black/15 backdrop-blur-xl px-4 sm:px-6 py-3 text-white">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">𓂀</span>
          <div>
            <h1 className="text-sm font-semibold text-white">Historia AI</h1>
            <p className="text-[11px] text-white/55 -mt-0.5">Egyptian history, grounded in sources</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <div className="relative z-10 border-b border-white/10 bg-black/10 backdrop-blur-md px-4 sm:px-6">
        <EraTimeline />
      </div>

      <div className="relative z-10 flex flex-1 min-h-0">
        <div className="hidden lg:flex w-[27%] min-w-72 flex-col justify-end p-8 text-white pointer-events-none">
          <div className="era-caption">
            <div className="text-5xl opacity-80">{theme.motif}</div>
            <p className="mt-4 text-xs uppercase tracking-[0.28em] text-white/50">Current destination</p>
            <h2 className="mt-2 text-2xl font-semibold">{theme.arabicLabel}</h2>
            <p className="mt-1 text-sm text-white/65">{theme.label} · {theme.range}</p>
            <p className="mt-3 text-xs leading-5 text-white/45">{theme.scene}</p>
          </div>
        </div>
        <main className="flex flex-1 min-w-0 m-2 sm:m-4 lg:ml-0 rounded-3xl border border-white/10 bg-[var(--era-surface)] shadow-2xl backdrop-blur-xl overflow-hidden">
          <ChatWindow />
        </main>
      </div>
    </div>
  );
}
