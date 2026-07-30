import { create } from "zustand";

import { ApiError, postChat } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

interface ChatState {
  messages: ChatMessage[];
  selectedEra: string | null;
  isSending: boolean;
  setEra: (era: string | null) => void;
  sendMessage: (question: string) => Promise<void>;
}

let nextId = 0;
const makeId = () => `msg-${++nextId}-${Date.now()}`;

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  selectedEra: null,
  isSending: false,

  setEra: (era) => set({ selectedEra: era }),

  sendMessage: async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || get().isSending) return;

    const era = get().selectedEra;
    const userMessage: ChatMessage = { id: makeId(), role: "user", text: trimmed, era };
    const pendingId = makeId();
    const pendingMessage: ChatMessage = { id: pendingId, role: "assistant", text: "", pending: true };

    set((state) => ({
      messages: [...state.messages, userMessage, pendingMessage],
      isSending: true,
    }));

    try {
      const response = await postChat(trimmed, era);
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === pendingId
            ? { ...m, text: response.answer, sources: response.sources, pending: false }
            : m
        ),
        isSending: false,
      }));
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === pendingId ? { ...m, pending: false, error: message } : m
        ),
        isSending: false,
      }));
    }
  },
}));
