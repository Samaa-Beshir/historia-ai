"use client";

import { useEffect, useRef, useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { EraTimeline } from "@/components/EraTimeline";
import { ThemeToggle } from "@/components/ThemeToggle";
import { WorkspacePanel, type WorkspaceView } from "@/components/WorkspacePanel";
import { getEraTheme } from "@/lib/eras";
import { useChatStore } from "@/store/chatStore";

type UiLanguage = "en" | "ar";
const NAV_ITEMS = [
  { view: "history", icon: "◷", en: "History", ar: "السجل" },
  { view: "bookmarks", icon: "◇", en: "Bookmarks", ar: "المحفوظات" },
  { view: "sources", icon: "▤", en: "Sources", ar: "المصادر" },
  { view: "timeline", icon: "⌛", en: "Timeline", ar: "الخط الزمني" },
  { view: "notes", icon: "✎", en: "My Notes", ar: "ملاحظاتي" },
] as const;

export function ChatApp() {
  const activeEra = useChatStore((s) => s.activeEra);
  const resetChat = useChatStore((s) => s.resetChat);
  const theme = getEraTheme(activeEra);
  const previousEra = useRef(activeEra);
  const hasTravelled = useRef(false);
  const [isTraveling, setIsTraveling] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [language, setLanguage] = useState<UiLanguage>("en");
  const [activeView, setActiveView] = useState<WorkspaceView | null>(null);

  useEffect(() => {
    if (previousEra.current === activeEra) return;
    previousEra.current = activeEra;
    setIsTraveling(true);
    const duration = hasTravelled.current ? 1100 : 2200;
    hasTravelled.current = true;
    const timer = window.setTimeout(() => setIsTraveling(false), duration);
    return () => window.clearTimeout(timer);
  }, [activeEra]);

  const isArabic = language === "ar";
  return (
    <div className="historia-shell" dir={isArabic ? "rtl" : "ltr"} style={{
      "--accent": theme.accent, "--accent-soft": theme.accentSoft, "--on-accent": theme.onAccent,
      "--era-glow": theme.glow, "--era-surface": theme.surface, "--era-background": theme.background,
      "--era-image": `url(${theme.image})`,
    } as React.CSSProperties}>
      <div className="era-atmosphere" aria-hidden="true" />
      {isTraveling && <div className="time-travel-overlay" role="status" aria-live="polite">
        <div className="portal-ring"><span>{theme.motif}</span></div>
        <p>{isArabic ? "جارٍ الانتقال عبر الزمن" : "Travelling through time"}</p>
        <h2>{isArabic ? theme.arabicLabel : theme.label}</h2><small>{theme.range}</small>
      </div>}
      {sidebarOpen && <button className="sidebar-scrim" aria-label="Close menu" onClick={() => setSidebarOpen(false)} />}

      <aside className={`historia-sidebar ${sidebarOpen ? "is-open" : ""}`}>
        <div className="brand-lockup"><span className="brand-mark">𓂀</span><div>
          <strong>HISTORIA AI</strong><small>{isArabic ? "مساعدك للبحث التاريخي" : "Your AI Historical Research Assistant"}</small>
        </div></div>
        <button className="new-chat-button" onClick={() => { resetChat(); setActiveView(null); setSidebarOpen(false); }}><span>▰</span>{isArabic ? "محادثة جديدة" : "New Chat"}</button>
        <nav className="side-navigation" aria-label="Primary navigation">
          {NAV_ITEMS.map((item) => <button key={item.en} className={activeView === item.view ? "active" : ""}
            onClick={() => { setActiveView(activeView === item.view ? null : item.view); setSidebarOpen(false); }}>
            <span>{item.icon}</span>{isArabic ? item.ar : item.en}<small>›</small>
          </button>)}
        </nav>
        <div className="sidebar-spacer" />
        <div className="era-detected-card"><small>{isArabic ? "الحقبة الحالية" : "ERA DETECTED"}</small>
          <span className="era-card-motif">{theme.motif}</span><strong>{isArabic ? theme.arabicLabel : theme.label}</strong>
          <p>{theme.range || (isArabic ? "رحلة عبر تاريخ مصر" : "A journey through Egyptian history")}</p>
        </div>
        <div className="sidebar-footer">Historia AI · V2</div>
      </aside>

      <section className="historia-stage">
        <header className="top-command-bar">
          <button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open menu">☰</button>
          <div className="mobile-brand">𓂀 <strong>HISTORIA AI</strong></div>
          <div className="era-plaque"><span>{theme.motif}</span><div><strong>{isArabic ? theme.arabicLabel : theme.label}</strong>
            <small>{theme.range || (isArabic ? "كل العصور" : "ALL ERAS")}</small></div><span>{theme.motif}</span>
          </div>
          <div className="command-controls"><ThemeToggle />
            <button className="language-button" onClick={() => setLanguage(isArabic ? "en" : "ar")}>◎ <span>{isArabic ? "EN" : "ع"}</span></button>
            <button className="control-button" disabled title={isArabic ? "قريبًا" : "Coming soon"}>⚙</button>
          </div>
        </header>
        <main className="experience-body">
          <section className="chat-column"><div className="chat-heading">
            <span className="eyebrow">{isArabic ? "محادثة موثقة بالمصادر" : "SOURCE-GROUNDED CONVERSATION"}</span>
            <h1>{isArabic ? "استكشف تاريخ مصر" : "Explore Egyptian History"}</h1>
            <p>{isArabic ? "اسأل بأي لغة، وسنبحث في المصادر التاريخية." : "Ask in any language. Historia searches the historical record."}</p>
          </div><div className="chat-panel"><ChatWindow language={language} /></div></section>
          <aside className="scene-caption" aria-label="Era atmosphere"><span>{theme.motif}</span><p>“{theme.motto}”</p><small>{theme.scene}</small></aside>
          {activeView && <WorkspacePanel view={activeView} language={language} onClose={() => setActiveView(null)} />}
        </main>
        <footer className="timeline-dock"><EraTimeline language={language} /></footer>
      </section>
    </div>
  );
}
