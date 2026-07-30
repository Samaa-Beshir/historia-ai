"use client";

import { useEffect, useState } from "react";

import { getEras } from "@/lib/api";
import { orderEras } from "@/lib/eras";
import { useChatStore } from "@/store/chatStore";

export function EraTimeline() {
  const [eras, setEras] = useState<string[]>([]);
  const selectedEra = useChatStore((s) => s.selectedEra);
  const setEra = useChatStore((s) => s.setEra);

  useEffect(() => {
    getEras()
      .then((res) => setEras(res.eras))
      .catch(() => setEras([]));
  }, []);

  const themes = orderEras(eras);

  return (
    <div className="w-full overflow-x-auto">
      <div className="flex items-stretch gap-2 min-w-max px-1 py-2">
        <button
          onClick={() => setEra(null)}
          className={`shrink-0 rounded-xl border px-4 py-2 text-sm font-medium transition-all cursor-pointer ${
            selectedEra === null
              ? "border-transparent bg-[var(--accent)] text-[var(--on-accent)] shadow-sm"
              : "border-black/10 dark:border-white/10 text-neutral-500 hover:border-[var(--accent)]/40"
          }`}
        >
          All Eras
        </button>

        <div className="relative flex items-center gap-2">
          {themes.map((theme, index) => {
            const isSelected = selectedEra === theme.era;
            return (
              <button
                key={theme.era}
                onClick={() => setEra(isSelected ? null : theme.era)}
                title={theme.range}
                className={`group shrink-0 relative rounded-xl border px-4 py-2 text-left transition-all cursor-pointer ${
                  isSelected
                    ? "shadow-sm"
                    : "border-black/10 dark:border-white/10 hover:border-black/20 dark:hover:border-white/20"
                }`}
                style={
                  isSelected
                    ? { backgroundColor: theme.accent, color: theme.onAccent, borderColor: "transparent" }
                    : undefined
                }
              >
                {index > 0 && (
                  <span className="absolute -left-2 top-1/2 h-px w-2 -translate-y-1/2 bg-black/10 dark:bg-white/15" />
                )}
                <div className="text-sm font-medium whitespace-nowrap">{theme.label}</div>
                <div
                  className={`text-[11px] whitespace-nowrap ${
                    isSelected ? "opacity-80" : "opacity-50"
                  }`}
                >
                  {theme.range}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
