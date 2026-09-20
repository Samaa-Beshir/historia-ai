"use client";

import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { getSupabaseClient, isCloudSyncConfigured } from "@/lib/supabase";
import type { WorkspaceSnapshot } from "@/lib/types";
import { useChatStore } from "@/store/chatStore";

type SyncStatus = "offline" | "syncing" | "synced" | "error";

function snapshot(): WorkspaceSnapshot {
  const state = useChatStore.getState();
  return {
    messages: state.messages.filter((message) => !message.pending),
    selectedEra: state.selectedEra,
    activeEra: state.activeEra,
    currentSessionId: state.currentSessionId,
    sessions: state.sessions,
    bookmarks: state.bookmarks,
    notes: state.notes,
  };
}

function validWorkspace(value: unknown): value is WorkspaceSnapshot {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<WorkspaceSnapshot>;
  return Array.isArray(item.messages) && Array.isArray(item.sessions)
    && Array.isArray(item.bookmarks) && Array.isArray(item.notes);
}

export function CloudAccount({ language }: { language: "en" | "ar" }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<SyncStatus>("offline");
  const [menuOpen, setMenuOpen] = useState(false);
  const isArabic = language === "ar";

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) return;
    let alive = true;
    let activeUserId: string | null = null;
    let saveTimer: ReturnType<typeof setTimeout> | null = null;
    let lastPayload = "";

    const save = async (userId: string) => {
      const state = snapshot();
      const payload = JSON.stringify(state);
      if (payload === lastPayload) return;
      setStatus("syncing");
      const { error } = await supabase.from("user_workspaces").upsert(
        { user_id: userId, state, updated_at: new Date().toISOString() }, { onConflict: "user_id" }
      );
      if (!alive) return;
      if (error) { setStatus("error"); return; }
      lastPayload = payload; setStatus("synced");
    };

    const connect = async (nextUser: User | null) => {
      if (!alive) return;
      setUser(nextUser); activeUserId = nextUser?.id ?? null;
      if (!nextUser) { setStatus("offline"); return; }
      setStatus("syncing");
      const { data, error } = await supabase.from("user_workspaces").select("state").eq("user_id", nextUser.id).maybeSingle();
      if (!alive) return;
      if (error) { setStatus("error"); return; }
      if (validWorkspace(data?.state)) useChatStore.getState().mergeCloudWorkspace(data.state);
      await save(nextUser.id);
    };

    supabase.auth.getSession().then(({ data }) => void connect(data.session?.user ?? null));
    const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
      window.setTimeout(() => void connect(session?.user ?? null), 0);
    });
    const unsubscribeStore = useChatStore.subscribe(() => {
      if (!activeUserId) return;
      if (saveTimer) clearTimeout(saveTimer);
      saveTimer = setTimeout(() => { if (activeUserId) void save(activeUserId); }, 900);
    });
    return () => {
      alive = false; authListener.subscription.unsubscribe(); unsubscribeStore();
      if (saveTimer) clearTimeout(saveTimer);
    };
  }, []);

  const signIn = async () => {
    const supabase = getSupabaseClient();
    if (!supabase) return;
    await supabase.auth.signInWithOAuth({ provider: "google", options: { redirectTo: window.location.origin } });
  };
  const signOut = async () => {
    const supabase = getSupabaseClient();
    if (!supabase) return;
    await supabase.auth.signOut(); setMenuOpen(false);
  };

  if (!isCloudSyncConfigured) return <button className="account-button setup" disabled title="Cloud sync is not configured">☁</button>;
  if (!user) return <button className="google-login" onClick={() => void signIn()}><b>G</b><span>{isArabic ? "الدخول" : "Sign in"}</span></button>;

  const avatar = typeof user.user_metadata.avatar_url === "string" ? user.user_metadata.avatar_url : null;
  const name = typeof user.user_metadata.full_name === "string" ? user.user_metadata.full_name : user.email ?? "Historia explorer";
  const statusLabel = status === "synced" ? (isArabic ? "تمت المزامنة" : "Synced")
    : status === "syncing" ? (isArabic ? "جارٍ الحفظ…" : "Saving…")
    : status === "error" ? (isArabic ? "خطأ في المزامنة" : "Sync error") : (isArabic ? "غير متصل" : "Offline");

  return <div className="account-menu-wrap">
    <button className="account-button" onClick={() => setMenuOpen((open) => !open)} aria-label={isArabic ? "الحساب" : "Account"}>
      {avatar ? <span style={{ backgroundImage: `url(${avatar})` }} /> : name.charAt(0).toUpperCase()}
      <i className={`sync-dot ${status}`} />
    </button>
    {menuOpen && <div className="account-popover">
      <strong>{name}</strong><small>{user.email}</small><p><i className={`sync-dot ${status}`} />{statusLabel}</p>
      <button onClick={() => void signOut()}>{isArabic ? "تسجيل الخروج" : "Sign out"}</button>
    </div>}
  </div>;
}
