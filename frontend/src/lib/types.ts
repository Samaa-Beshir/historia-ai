export interface SourceRef {
  document_id: string;
  title: string;
  author: string;
  era: string;
  source_type: "book" | "research_paper";
  snippet: string;
  relevance: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceRef[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: SourceRef[];
  era?: string | null;
  pending?: boolean;
  error?: string;
}

export interface ConversationSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  selectedEra: string | null;
  createdAt: number;
  updatedAt: number;
}

export interface SavedBookmark {
  id: string;
  message: ChatMessage;
  createdAt: number;
}

export interface HistoriaNote {
  id: string;
  text: string;
  era: string | null;
  createdAt: number;
}

export interface DocumentSummary {
  document_id: string;
  title: string;
  author: string;
  era: string;
  source_type: "book" | "research_paper";
  page_count: number;
}
