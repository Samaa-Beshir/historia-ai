"use client";

import { Fragment, type ReactNode, useEffect, useState } from "react";

import type { ChatMessage } from "@/lib/types";

// The API is hosted on a free tier that sleeps after inactivity and takes about
// a minute to wake. Past this point a silent spinner reads as a broken app, so
// explain the wait instead.
const COLD_START_HINT_MS = 5000;
const ARABIC_CHARACTERS = /[\u0600-\u06ff]/;

export function isArabicText(text: string) {
  return ARABIC_CHARACTERS.test(text);
}

function renderInlineMarkdown(text: string): ReactNode[] {
  const tokens = text.split(/(\*\*[^*]+\*\*|\[[0-9]+\])/g);

  return tokens.filter(Boolean).map((token, index) => {
    if (token.startsWith("**") && token.endsWith("**")) {
      return <strong key={index} className="font-semibold">{token.slice(2, -2)}</strong>;
    }
    if (/^\[[0-9]+\]$/.test(token)) {
      return <span key={index} className="font-semibold text-[var(--accent)]">{token}</span>;
    }
    return <Fragment key={index}>{token}</Fragment>;
  });
}

function MarkdownAnswer({ text }: { text: string }) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");

  return (
    <div className="answer-arrival space-y-2.5">
      {lines.map((rawLine, index) => {
        const line = rawLine.trim();
        if (!line) return null;

        const heading = line.match(/^#{1,3}\s+(.+)$/);
        const bullet = line.match(/^[-*]\s+(.+)$/);
        const numbered = line.match(/^(\d+)[.)]\s+(.+)$/);
        const boldHeading = line.match(/^\*\*(.+)\*\*$/);

        if (heading || boldHeading) {
          const content = heading?.[1] ?? boldHeading?.[1] ?? line;
          return <h3 key={index} className="pt-1 text-[0.95rem] font-semibold">{renderInlineMarkdown(content)}</h3>;
        }

        if (bullet) {
          return (
            <div key={index} className="flex items-start gap-2">
              <span aria-hidden="true" className="mt-[0.1em] text-[var(--accent)]">•</span>
              <span className="min-w-0">{renderInlineMarkdown(bullet[1])}</span>
            </div>
          );
        }

        if (numbered) {
          return (
            <div key={index} className="flex items-start gap-2">
              <span className="font-semibold text-[var(--accent)]">{numbered[1]}.</span>
              <span className="min-w-0">{renderInlineMarkdown(numbered[2])}</span>
            </div>
          );
        }

        return <p key={index}>{renderInlineMarkdown(line)}</p>;
      })}
    </div>
  );
}

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
        جاري تشغيل الخادم، قد يستغرق ذلك دقيقة — Waking the server up.
      </span>
    </span>
  );
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";
  const displayedText = message.error ?? message.text;
  const isArabic = isArabicText(displayedText);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[92%] sm:max-w-[78%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1.5`}>
        <div
          dir={isArabic ? "rtl" : "ltr"}
          lang={isArabic ? "ar" : "en"}
          className={`w-full rounded-2xl px-4 py-3 text-sm leading-7 ${isArabic ? "text-right" : "text-left"} ${
            isUser
              ? "bg-[var(--accent)] text-[var(--on-accent)] rounded-br-sm"
              : "bg-white/[0.08] text-white rounded-bl-sm border border-white/[0.06]"
          }`}
        >
          {message.pending ? (
            <PendingIndicator />
          ) : message.error ? (
            message.error
          ) : isUser ? (
            message.text
          ) : (
            <MarkdownAnswer text={message.text} />
          )}
        </div>

        {!isUser && !message.pending && message.sources && message.sources.length > 0 && (
          <div className="w-full" dir={isArabic ? "rtl" : "ltr"}>
            <button
              onClick={() => setShowSources((v) => !v)}
              className="text-xs text-white/50 hover:text-white/85 cursor-pointer underline decoration-dotted underline-offset-2"
            >
              {isArabic
                ? `${showSources ? "إخفاء" : "عرض"} ${message.sources.length} مصادر`
                : `${showSources ? "Hide" : "Show"} ${message.sources.length} source${message.sources.length === 1 ? "" : "s"}`}
            </button>
            {showSources && (
              <ul className="mt-2 flex flex-col gap-2">
                {message.sources.map((source, i) => {
                  const sourceIsArabic = isArabicText(`${source.title} ${source.author} ${source.snippet}`);
                  return (
                    <li
                      key={`${source.document_id}-${i}`}
                      dir={sourceIsArabic ? "rtl" : "ltr"}
                      className={`rounded-xl border border-white/10 px-3 py-2 text-xs bg-black/20 ${sourceIsArabic ? "text-right" : "text-left"}`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium text-white/90">
                          [{i + 1}] {source.title}
                        </span>
                        <span className="shrink-0 rounded-full bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-0.5 text-[10px] font-medium">
                          {source.era}
                        </span>
                      </div>
                      <div className="mt-0.5 text-white/45">{source.author}</div>
                      <p className="mt-1 text-white/60 line-clamp-3">{source.snippet}</p>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
