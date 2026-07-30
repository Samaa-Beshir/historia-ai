"use client";

import { useEffect, useRef, useState } from "react";

import { MessageBubble } from "@/components/MessageBubble";
import { useChatStore } from "@/store/chatStore";

export function ChatWindow() {
  const messages = useChatStore((s) => s.messages);
  const isSending = useChatStore((s) => s.isSending);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

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
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 flex flex-col gap-4">
        {messages.length === 0 ? (
          <div className="m-auto text-center max-w-sm">
            <div className="text-4xl mb-3">📜</div>
            <h2 className="text-base font-medium text-neutral-700 dark:text-neutral-200">
              Ask Historia AI about Egyptian history
            </h2>
            <p className="mt-1.5 text-sm text-neutral-500">
              Pick an era above to travel there, or ask across all eras. Every answer is grounded in
              the sources you selected.
            </p>
          </div>
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-black/10 dark:border-white/10 p-3 sm:p-4">
        <div className="flex items-center gap-2 rounded-2xl border border-black/10 dark:border-white/10 bg-white dark:bg-neutral-900 px-2 py-1.5 focus-within:border-[var(--accent)] transition-colors">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Egyptian history..."
            className="flex-1 bg-transparent px-2 py-2 text-sm outline-none placeholder:text-neutral-400"
          />
          <button
            type="submit"
            disabled={!input.trim() || isSending}
            className="shrink-0 rounded-xl bg-[var(--accent)] text-[var(--on-accent)] px-4 py-2 text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-opacity"
          >
            {isSending ? "..." : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
