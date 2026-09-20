-- One private JSON workspace per authenticated Historia user.
-- Run this once in Supabase Dashboard > SQL Editor.
create table if not exists public.user_workspaces (
  user_id uuid primary key references auth.users(id) on delete cascade,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.user_workspaces enable row level security;

create policy "Users can read their own Historia workspace"
on public.user_workspaces for select to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can create their own Historia workspace"
on public.user_workspaces for insert to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update their own Historia workspace"
on public.user_workspaces for update to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete their own Historia workspace"
on public.user_workspaces for delete to authenticated
using ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.user_workspaces to authenticated;
