"use client";

import { ChatWindow } from "@/components/ChatWindow";
import { EraTimeline } from "@/components/EraTimeline";
import { ThemeToggle } from "@/components/ThemeToggle";
import { getEraTheme } from "@/lib/eras";
import { useChatStore } from "@/store/chatStore";

export function ChatApp() {
  const selectedEra = useChatStore((s) => s.selectedEra);
  const theme = getEraTheme(selectedEra);

  return (
    <div
      className="flex flex-col flex-1 min-h-0 transition-colors duration-500"
      style={
        {
          "--accent": theme.accent,
          "--accent-soft": theme.accentSoft,
          "--on-accent": theme.onAccent,
        } as React.CSSProperties
      }
    >
      <header className="flex items-center justify-between gap-4 border-b border-black/10 dark:border-white/10 px-4 sm:px-6 py-3">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">𓂀</span>
          <div>
            <h1 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">Historia AI</h1>
            <p className="text-[11px] text-neutral-500 -mt-0.5">Egyptian history, grounded in sources</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <div className="border-b border-black/10 dark:border-white/10 px-4 sm:px-6">
        <EraTimeline />
      </div>

      <ChatWindow />
    </div>
  );
}
