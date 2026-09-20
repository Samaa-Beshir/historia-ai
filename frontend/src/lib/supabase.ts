import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const isCloudSyncConfigured = Boolean(supabaseUrl && supabaseKey);
let browserClient: SupabaseClient | null = null;

export function getSupabaseClient() {
  if (!isCloudSyncConfigured || !supabaseUrl || !supabaseKey) return null;
  if (!browserClient) {
    browserClient = createClient(supabaseUrl, supabaseKey, {
      auth: { persistSession: true, detectSessionInUrl: true, flowType: "implicit" },
    });
  }
  return browserClient;
}
