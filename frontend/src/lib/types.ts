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

export interface DocumentSummary {
  document_id: string;
  title: string;
  author: string;
  era: string;
  source_type: "book" | "research_paper";
  page_count: number;
}
