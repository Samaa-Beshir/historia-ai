"use client";

import { useEffect, useState } from "react";

import type { ChatMessage } from "@/lib/types";

// The API is hosted on a free tier that sleeps after inactivity and takes about
// a minute to wake. Past this point a silent spinner reads as a broken app, so
// explain the wait instead.
const COLD_START_HINT_MS = 5000;

function TypingDots() {
  return (
    <span className="inline-flex gap-1 items-center py-1">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-current opacity-60 animate-bounce"
          style={{ animationDelay: `${i * 120}ms` }}
        />
      ))}
    </span>
  );
}

function PendingIndicator() {
  const [slow, setSlow] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), COLD_START_HINT_MS);
    return () => clearTimeout(timer);
  }, []);

  if (!slow) return <TypingDots />;

  return (
    <span className="inline-flex items-center gap-2">
      <TypingDots />
      <span className="text-xs text-neutral-500">
        Waking the server up — this can take a minute.
      </span>
    </span>
  );
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] sm:max-w-[70%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1.5`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? "bg-[var(--accent)] text-[var(--on-accent)] rounded-br-sm"
              : "bg-black/[0.04] dark:bg-white/[0.06] text-neutral-900 dark:text-neutral-100 rounded-bl-sm"
          }`}
        >
          {message.pending ? <PendingIndicator /> : message.error ? message.error : message.text}
        </div>

        {!isUser && !message.pending && message.sources && message.sources.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setShowSources((v) => !v)}
              className="text-xs text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200 cursor-pointer underline decoration-dotted underline-offset-2"
            >
              {showSources ? "Hide" : "Show"} {message.sources.length} source
              {message.sources.length === 1 ? "" : "s"}
            </button>
            {showSources && (
              <ul className="mt-2 flex flex-col gap-2">
                {message.sources.map((source, i) => (
                  <li
                    key={`${source.document_id}-${i}`}
                    className="rounded-lg border border-black/10 dark:border-white/10 px-3 py-2 text-xs bg-white/60 dark:bg-black/20"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-neutral-800 dark:text-neutral-100">
                        [{i + 1}] {source.title}
                      </span>
                      <span className="shrink-0 rounded-full bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-0.5 text-[10px] font-medium">
                        {source.era}
                      </span>
                    </div>
                    <div className="mt-0.5 text-neutral-500">{source.author}</div>
                    <p className="mt-1 text-neutral-600 dark:text-neutral-400 line-clamp-3">{source.snippet}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
