"use client";

import { useEffect, useState } from "react";
import { getDocuments } from "@/lib/api";
import { ERA_THEMES } from "@/lib/eras";
import type { DocumentSummary } from "@/lib/types";
import { useChatStore } from "@/store/chatStore";

export type WorkspaceView = "history" | "bookmarks" | "sources" | "timeline" | "notes";

const TITLES: Record<WorkspaceView, { en: string; ar: string }> = {
  history: { en: "Conversation History", ar: "سجل المحادثات" },
  bookmarks: { en: "Saved Answers", ar: "الإجابات المحفوظة" },
  sources: { en: "Source Library", ar: "مكتبة المصادر" },
  timeline: { en: "Historical Timeline", ar: "الخط الزمني" },
  notes: { en: "My Research Notes", ar: "ملاحظاتي البحثية" },
};

const when = (timestamp: number, language: "en" | "ar") => new Intl.DateTimeFormat(
  language === "ar" ? "ar-EG" : "en-GB", { dateStyle: "medium", timeStyle: "short" }
).format(timestamp);

export function WorkspacePanel({ view, language, onClose }: {
  view: WorkspaceView;
  language: "en" | "ar";
  onClose: () => void;
}) {
  const sessions = useChatStore((state) => state.sessions);
  const bookmarks = useChatStore((state) => state.bookmarks);
  const notes = useChatStore((state) => state.notes);
  const selectedEra = useChatStore((state) => state.selectedEra);
  const loadSession = useChatStore((state) => state.loadSession);
  const deleteSession = useChatStore((state) => state.deleteSession);
  const toggleBookmark = useChatStore((state) => state.toggleBookmark);
  const addNote = useChatStore((state) => state.addNote);
  const deleteNote = useChatStore((state) => state.deleteNote);
  const setEra = useChatStore((state) => state.setEra);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(view === "sources");
  const [documentError, setDocumentError] = useState(false);
  const [noteDraft, setNoteDraft] = useState("");
  const isArabic = language === "ar";

  useEffect(() => {
    if (view !== "sources") return;
    getDocuments(selectedEra).then((result) => setDocuments(result.documents))
      .catch(() => setDocumentError(true)).finally(() => setLoadingDocuments(false));
  }, [view, selectedEra]);

  const empty = (en: string, ar: string) => <div className="workspace-empty"><span>⌛</span><p>{isArabic ? ar : en}</p></div>;

  return <section className="workspace-panel" aria-label={TITLES[view][language]}>
    <header><div><small>HISTORIA WORKSPACE</small><h2>{TITLES[view][language]}</h2></div>
      <button onClick={onClose} aria-label={isArabic ? "إغلاق" : "Close"}>×</button>
    </header>
    <div className="workspace-content">
      {view === "history" && (sessions.length === 0 ? empty("Your conversations will appear here.", "ستظهر محادثاتك هنا.") :
        <div className="workspace-list">{sessions.map((session) => <article className="workspace-item" key={session.id}>
          <button className="workspace-item-main" onClick={() => { loadSession(session.id); onClose(); }}>
            <span className="item-icon">◷</span><span><strong>{session.title}</strong>
            <small>{when(session.updatedAt, language)}{session.selectedEra ? ` · ${session.selectedEra}` : ""}</small></span>
          </button><button className="item-delete" onClick={() => deleteSession(session.id)} aria-label={isArabic ? "حذف المحادثة" : "Delete conversation"}>×</button>
        </article>)}</div>)}

      {view === "bookmarks" && (bookmarks.length === 0 ? empty("Save any Historia answer to revisit it here.", "احفظي أي إجابة من Historia لتعودي إليها هنا.") :
        <div className="workspace-list">{bookmarks.map((bookmark) => <article className="saved-answer" key={bookmark.id}>
          <div><span className="item-icon">◇</span><small>{when(bookmark.createdAt, language)}</small>
            <button className="item-delete" onClick={() => toggleBookmark(bookmark.message)}>×</button></div>
          <p dir={/[؀-ۿ]/.test(bookmark.message.text) ? "rtl" : "ltr"}>{bookmark.message.text}</p>
        </article>)}</div>)}

      {view === "sources" && (loadingDocuments ? empty("Opening the source library…", "جارٍ فتح مكتبة المصادر…") : documentError ?
        empty("The library could not be reached. Please try again.", "تعذر الوصول إلى المكتبة. حاولي مرة أخرى.") :
        <><div className="library-summary"><span>▤</span><div><strong>{documents.length}</strong><small>{isArabic ? " مصدر متاح" : " available sources"}</small></div>
          {selectedEra && <em>{selectedEra}</em>}</div>
        <div className="document-grid">{documents.map((document) => <article key={document.document_id}>
          <span>{document.source_type === "book" ? "▥" : "⌁"}</span><div><strong>{document.title}</strong><p>{document.author}</p>
          <small>{document.era} · {document.page_count} {isArabic ? "صفحة" : "pages"}</small></div>
        </article>)}</div></>)}

      {view === "timeline" && <div className="timeline-grid">{ERA_THEMES.map((theme, index) => <button key={theme.era} onClick={() => { setEra(theme.era); onClose(); }}>
        <span className="timeline-number">0{index + 1}</span><span className="timeline-symbol">{theme.motif}</span><span>
          <strong>{isArabic ? theme.arabicLabel : theme.label}</strong><small>{theme.range}</small><p>{theme.scene}</p>
        </span></button>)}</div>}

      {view === "notes" && <><form className="note-composer" onSubmit={(event) => { event.preventDefault(); addNote(noteDraft); setNoteDraft(""); }}>
        <textarea value={noteDraft} onChange={(event) => setNoteDraft(event.target.value)} dir={isArabic ? "rtl" : "ltr"}
          placeholder={isArabic ? "اكتبي ملاحظة أثناء البحث…" : "Write a note while you research…"} />
        <button disabled={!noteDraft.trim()}>{isArabic ? "حفظ الملاحظة" : "Save note"}</button>
      </form>{notes.length === 0 ? empty("Your research notes will stay on this device.", "ستظل ملاحظاتك البحثية محفوظة على هذا الجهاز.") :
        <div className="notes-grid">{notes.map((note) => <article key={note.id}><div><small>{when(note.createdAt, language)}{note.era ? ` · ${note.era}` : ""}</small>
          <button onClick={() => deleteNote(note.id)}>×</button></div><p dir={/[؀-ۿ]/.test(note.text) ? "rtl" : "ltr"}>{note.text}</p></article>)}</div>}</>}
    </div>
  </section>;
}
