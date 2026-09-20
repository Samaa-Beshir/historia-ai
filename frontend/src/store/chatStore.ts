import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { ApiError, postChat } from "@/lib/api";
import type { ChatMessage, ConversationSession, HistoriaNote, SavedBookmark, WorkspaceSnapshot } from "@/lib/types";

interface ChatState {
  messages: ChatMessage[];
  selectedEra: string | null;
  activeEra: string | null;
  isSending: boolean;
  currentSessionId: string | null;
  sessions: ConversationSession[];
  bookmarks: SavedBookmark[];
  notes: HistoriaNote[];
  setEra: (era: string | null) => void;
  resetChat: () => void;
  loadSession: (id: string) => void;
  deleteSession: (id: string) => void;
  toggleBookmark: (message: ChatMessage) => void;
  addNote: (text: string) => void;
  deleteNote: (id: string) => void;
  mergeCloudWorkspace: (workspace: WorkspaceSnapshot) => void;
  sendMessage: (question: string) => Promise<void>;
}

let nextId = 0;
const makeId = (prefix = "msg") => `${prefix}-${Date.now()}-${++nextId}`;
const conversationTitle = (messages: ChatMessage[]) => {
  const question = messages.find((message) => message.role === "user")?.text.trim();
  if (!question) return "New historical journey";
  return question.length > 52 ? `${question.slice(0, 52)}…` : question;
};

function upsertSession(
  sessions: ConversationSession[],
  id: string,
  messages: ChatMessage[],
  selectedEra: string | null,
) {
  const now = Date.now();
  const existing = sessions.find((session) => session.id === id);
  const session: ConversationSession = {
    id,
    title: conversationTitle(messages),
    messages,
    selectedEra,
    createdAt: existing?.createdAt ?? now,
    updatedAt: now,
  };
  return [session, ...sessions.filter((item) => item.id !== id)].slice(0, 30);
}

export const useChatStore = create<ChatState>()(persist((set, get) => ({
  messages: [], selectedEra: null, activeEra: null, isSending: false,
  currentSessionId: null, sessions: [], bookmarks: [], notes: [],

  setEra: (era) => set((state) => ({
    selectedEra: era,
    activeEra: era,
    sessions: state.currentSessionId
      ? upsertSession(state.sessions, state.currentSessionId, state.messages, era)
      : state.sessions,
  })),

  resetChat: () => set({ messages: [], selectedEra: null, activeEra: null, isSending: false, currentSessionId: null }),

  loadSession: (id) => set((state) => {
    const session = state.sessions.find((item) => item.id === id);
    if (!session) return state;
    return { messages: session.messages, selectedEra: session.selectedEra, activeEra: session.selectedEra, currentSessionId: id, isSending: false };
  }),

  deleteSession: (id) => set((state) => ({
    sessions: state.sessions.filter((session) => session.id !== id),
    ...(state.currentSessionId === id ? { messages: [], currentSessionId: null, selectedEra: null, activeEra: null } : {}),
  })),

  toggleBookmark: (message) => set((state) => {
    const existing = state.bookmarks.find((bookmark) => bookmark.message.id === message.id);
    return { bookmarks: existing
      ? state.bookmarks.filter((bookmark) => bookmark.id !== existing.id)
      : [{ id: makeId("bookmark"), message, createdAt: Date.now() }, ...state.bookmarks]
    };
  }),

  addNote: (text) => set((state) => {
    const clean = text.trim();
    if (!clean) return state;
    return { notes: [{ id: makeId("note"), text: clean, era: state.activeEra, createdAt: Date.now() }, ...state.notes] };
  }),
  deleteNote: (id) => set((state) => ({ notes: state.notes.filter((note) => note.id !== id) })),

  mergeCloudWorkspace: (remote) => set((state) => {
    const sessions = [...state.sessions, ...remote.sessions].reduce<ConversationSession[]>((merged, session) => {
      const existing = merged.find((item) => item.id === session.id);
      if (!existing) return [...merged, session];
      return existing.updatedAt >= session.updatedAt ? merged : merged.map((item) => item.id === session.id ? session : item);
    }, []).sort((a, b) => b.updatedAt - a.updatedAt).slice(0, 30);
    const bookmarks = [...state.bookmarks, ...remote.bookmarks].filter((bookmark, index, all) =>
      all.findIndex((item) => item.message.id === bookmark.message.id) === index
    );
    const notes = [...state.notes, ...remote.notes].filter((note, index, all) =>
      all.findIndex((item) => item.id === note.id) === index
    );
    const useRemoteCurrent = state.messages.length === 0 && remote.messages.length > 0;
    return {
      sessions, bookmarks, notes,
      ...(useRemoteCurrent ? {
        messages: remote.messages,
        selectedEra: remote.selectedEra,
        activeEra: remote.activeEra,
        currentSessionId: remote.currentSessionId,
      } : {}),
    };
  }),

  sendMessage: async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || get().isSending) return;
    const era = get().selectedEra;
    const sessionId = get().currentSessionId ?? makeId("chat");
    const userMessage: ChatMessage = { id: makeId(), role: "user", text: trimmed, era };
    const pendingId = makeId();
    const pendingMessage: ChatMessage = { id: pendingId, role: "assistant", text: "", pending: true };

    set((state) => {
      const messages = [...state.messages, userMessage, pendingMessage];
      return { messages, currentSessionId: sessionId, sessions: upsertSession(state.sessions, sessionId, messages, era), isSending: true };
    });

    try {
      const response = await postChat(trimmed, era);
      const detectedEra = response.sources.reduce<Record<string, number>>((scores, source) => {
        scores[source.era] = (scores[source.era] ?? 0) + Math.max(source.relevance, 0.01);
        return scores;
      }, {});
      const dominantEra = Object.entries(detectedEra).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
      set((state) => {
        const messages = state.messages.map((message) => message.id === pendingId
          ? { ...message, text: response.answer, sources: response.sources, pending: false }
          : message);
        const activeEra = state.selectedEra ?? dominantEra ?? state.activeEra;
        return { messages, activeEra, sessions: upsertSession(state.sessions, sessionId, messages, state.selectedEra), isSending: false };
      });
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
      set((state) => {
        const messages = state.messages.map((item) => item.id === pendingId ? { ...item, pending: false, error: message } : item);
        return { messages, sessions: upsertSession(state.sessions, sessionId, messages, state.selectedEra), isSending: false };
      });
    }
  },
}), {
  name: "historia-v2-workspace",
  storage: createJSONStorage(() => localStorage),
  partialize: (state) => ({
    messages: state.messages, selectedEra: state.selectedEra, activeEra: state.activeEra,
    currentSessionId: state.currentSessionId, sessions: state.sessions,
    bookmarks: state.bookmarks, notes: state.notes,
  }),
}));
