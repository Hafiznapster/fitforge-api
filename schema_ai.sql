-- AI Interactions Table
create table public.ai_interactions (
  id           uuid default gen_random_uuid() primary key,
  user_id      uuid references auth.users(id) on delete cascade not null,
  task_type    text not null, -- 'chat', 'plan', 'suggest'
  prompt       text not null,
  response     text not null,
  provider     text not null,
  created_at   timestamptz default now()
);

alter table public.ai_interactions enable row level security;
create policy "Users manage own AI interactions" on ai_interactions for all using (auth.uid() = user_id);
create index idx_ai_user_date on ai_interactions(user_id, created_at);
