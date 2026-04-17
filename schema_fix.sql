-- =============================================================================
-- FITFORGE SCHEMA SETUP (Safe to re-run - idempotent)
-- Run this entire script in: Supabase Dashboard → SQL Editor → New Query
-- =============================================================================

-- profiles table (extends Supabase auth.users)
create table if not exists public.profiles (
  id           uuid references auth.users(id) on delete cascade primary key,
  username     text unique not null,
  full_name    text,
  avatar_url   text,
  age          int,
  gender       text check (gender in ('male', 'female', 'other')),
  height_cm    numeric(5,1),
  weight_kg    numeric(5,1),
  activity_level text default 'moderate',
  goal         text default 'maintain',
  calorie_goal int default 2000,
  protein_goal int default 150,
  carb_goal    int default 200,
  fat_goal     int default 65,
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

-- Enable RLS
alter table public.profiles enable row level security;

-- Drop and recreate policies so re-running is safe
drop policy if exists "Users can view own profile" on profiles;
drop policy if exists "Users can update own profile" on profiles;
drop policy if exists "Users can insert own profile" on profiles;

create policy "Users can view own profile"   on profiles for select using (auth.uid() = id);
create policy "Users can update own profile" on profiles for update using (auth.uid() = id);
create policy "Users can insert own profile" on profiles for insert with check (auth.uid() = id);

-- Meals & Food Log
create table if not exists public.meals (
  id           uuid default gen_random_uuid() primary key,
  user_id      uuid references auth.users(id) on delete cascade not null,
  name         text not null,
  calories     int not null,
  protein_g    numeric(6,1) default 0,
  carbs_g      numeric(6,1) default 0,
  fat_g        numeric(6,1) default 0,
  fiber_g      numeric(6,1) default 0,
  meal_type    text default 'snack',
  logged_at    timestamptz default now(),
  notes        text,
  created_at   timestamptz default now()
);

alter table public.meals enable row level security;
drop policy if exists "Users manage own meals" on meals;
create policy "Users manage own meals" on meals for all using (auth.uid() = user_id);
create index if not exists idx_meals_user_date on meals(user_id, logged_at);

-- Workouts & Exercises
create table if not exists public.workout_sessions (
  id           uuid default gen_random_uuid() primary key,
  user_id      uuid references auth.users(id) on delete cascade not null,
  name         text not null,
  type         text default 'strength',
  duration_min int,
  calories_burned int,
  notes        text,
  logged_at    timestamptz default now(),
  created_at   timestamptz default now()
);

create table if not exists public.workout_exercises (
  id              uuid default gen_random_uuid() primary key,
  session_id      uuid references workout_sessions(id) on delete cascade not null,
  user_id         uuid references auth.users(id) on delete cascade not null,
  exercise_name   text not null,
  sets            int default 3,
  reps            int,
  weight_kg       numeric(6,1),
  duration_sec    int,
  rest_sec        int default 90,
  notes           text,
  order_index     int default 0
);

alter table public.workout_sessions enable row level security;
alter table public.workout_exercises enable row level security;
drop policy if exists "Users manage own sessions" on workout_sessions;
drop policy if exists "Users manage own exercises" on workout_exercises;
create policy "Users manage own sessions" on workout_sessions for all using (auth.uid() = user_id);
create policy "Users manage own exercises" on workout_exercises for all using (auth.uid() = user_id);
create index if not exists idx_sessions_user_date on workout_sessions(user_id, logged_at);

-- Body Metrics & Water
create table if not exists public.body_metrics (
  id            uuid default gen_random_uuid() primary key,
  user_id       uuid references auth.users(id) on delete cascade not null,
  weight_kg     numeric(5,1),
  body_fat_pct  numeric(4,1),
  muscle_mass_kg numeric(5,1),
  waist_cm      numeric(5,1),
  logged_at     timestamptz default now()
);

create table if not exists public.water_logs (
  id        uuid default gen_random_uuid() primary key,
  user_id   uuid references auth.users(id) on delete cascade not null,
  glasses   int default 1,
  logged_at timestamptz default now()
);

alter table public.body_metrics enable row level security;
alter table public.water_logs enable row level security;
drop policy if exists "Users manage own metrics" on body_metrics;
drop policy if exists "Users manage own water" on water_logs;
create policy "Users manage own metrics" on body_metrics for all using (auth.uid() = user_id);
create policy "Users manage own water" on water_logs for all using (auth.uid() = user_id);

-- =============================================================================
-- AUTO-CREATE PROFILE ON USER REGISTRATION (THE KEY FIX)
-- This trigger runs when a new user signs up. It safely handles duplicate
-- usernames by appending a short unique suffix when needed.
-- =============================================================================
create or replace function public.handle_new_user()
returns trigger as $$
declare
  base_username text;
  final_username text;
  suffix int := 0;
begin
  -- Derive a base username from metadata or email prefix
  base_username := coalesce(
    new.raw_user_meta_data->>'username',
    split_part(new.email, '@', 1)
  );

  -- Clean the username: lowercase, remove special chars
  base_username := lower(regexp_replace(base_username, '[^a-zA-Z0-9_]', '', 'g'));

  -- Ensure it's not empty
  if base_username = '' then
    base_username := 'user';
  end if;

  final_username := base_username;

  -- Handle username collisions by appending a number
  while exists (select 1 from public.profiles where username = final_username) loop
    suffix := suffix + 1;
    final_username := base_username || suffix::text;
  end loop;

  insert into public.profiles (id, username, full_name)
  values (
    new.id,
    final_username,
    coalesce(new.raw_user_meta_data->>'full_name', '')
  );

  return new;
exception
  when others then
    -- Log the error but don't block user creation
    raise warning 'handle_new_user failed for %: %', new.id, sqlerrm;
    return new;
end;
$$ language plpgsql security definer;

-- Drop and recreate trigger (safe to re-run)
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
