"use client";
import { useEffect, useState } from "react";
import { getEras } from "@/lib/api";
import { orderEras } from "@/lib/eras";
import { useChatStore } from "@/store/chatStore";

export function EraTimeline({ language = "en" }: { language?: "en" | "ar" }) {
  const [eras, setEras] = useState<string[]>([]);
  const selectedEra = useChatStore((s) => s.selectedEra);
  const setEra = useChatStore((s) => s.setEra);
  useEffect(() => { getEras().then((res) => setEras(res.eras)).catch(() => setEras([])); }, []);
  return <div className="era-timeline" dir="ltr">
    <button className={`timeline-all ${selectedEra === null ? "active" : ""}`} onClick={() => setEra(null)}>
      <span>⌛</span><strong>{language === "ar" ? "كل العصور" : "All Eras"}</strong>
    </button>
    {orderEras(eras).map((theme) => {
      const active = selectedEra === theme.era;
      return <button key={theme.era} className={`timeline-era ${active ? "active" : ""}`} onClick={() => setEra(active ? null : theme.era)}>
        <span className="timeline-dot">{theme.motif}</span><span className="timeline-copy">
          <strong>{language === "ar" ? theme.arabicLabel : theme.label}</strong><small>{theme.range}</small>
        </span>
      </button>;
    })}
  </div>;
}
