"use client";

import { useEffect, useRef, useState } from "react";

import { isArabicText, MessageBubble } from "@/components/MessageBubble";
import { useChatStore } from "@/store/chatStore";

export function ChatWindow({ language = "en" }: { language?: "en" | "ar" }) {
  const messages = useChatStore((s) => s.messages);
  const isSending = useChatStore((s) => s.isSending);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputIsArabic = isArabicText(input);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;
    void sendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="chat-scroll flex-1 overflow-y-auto px-4 sm:px-5 py-5 flex flex-col gap-4">
        {messages.length === 0 ? (
          <div className="empty-conversation m-auto text-center max-w-md">
            <div className="empty-mark">𓂀</div>
            <h2 className="text-base font-medium text-white/90">
              {language === "ar" ? "اسأل Historia AI عن تاريخ مصر" : "Begin your journey through Egyptian history"}
            </h2>
            <p className="mt-1.5 text-sm text-white/60" dir={language === "ar" ? "rtl" : "ltr"}>
              {language === "ar" ? "اختر حقبة زمنية أو اسأل في جميع العصور. كل إجابة مبنية على المصادر التاريخية المتاحة." : "Choose an era or ask across all periods. Every answer is grounded in the available historical sources."}
            </p>
            <p className="mt-2 text-xs text-white/40">العربية & English</p>
          </div>
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="composer-wrap">
        <div className="composer">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            dir={inputIsArabic ? "rtl" : "ltr"}
            lang={inputIsArabic ? "ar" : "en"}
            aria-label="اسأل عن التاريخ المصري — Ask about Egyptian history"
            placeholder={language === "ar" ? "اسأل عن تاريخ مصر..." : "Ask about Egyptian history..."}
            className={`flex-1 bg-transparent px-2 py-2 text-sm text-white outline-none placeholder:text-white/35 ${inputIsArabic ? "text-right" : "text-left"}`}
          />
          <button
            type="submit"
            disabled={!input.trim() || isSending}
            className="send-button"
          >
            {isSending ? "…" : "➤"}
          </button>
        </div>
      </form>
    </div>
  );
}
