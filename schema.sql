-- profiles table (extends Supabase auth.users)
create table public.profiles (
  id           uuid references auth.users(id) on delete cascade primary key,
  username     text unique not null,
  full_name    text,
  avatar_url   text,
  age          int,
  gender       text check (gender in ('male', 'female', 'other')),
  height_cm    numeric(5,1),
  weight_kg    numeric(5,1),
  activity_level text default 'moderate',
  goal         text default 'maintain', -- 'cut', 'maintain', 'bulk'
  calorie_goal int default 2000,
  protein_goal int default 150,
  carb_goal    int default 200,
  fat_goal     int default 65,
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

-- Enable RLS
alter table public.profiles enable row level security;
create policy "Users can view own profile" on profiles for select using (auth.uid() = id);
create policy "Users can update own profile" on profiles for update using (auth.uid() = id);

-- Meals & Food Log
create table public.meals (
  id           uuid default gen_random_uuid() primary key,
  user_id      uuid references auth.users(id) on delete cascade not null,
  name         text not null,
  calories     int not null,
  protein_g    numeric(6,1) default 0,
  carbs_g      numeric(6,1) default 0,
  fat_g        numeric(6,1) default 0,
  fiber_g      numeric(6,1) default 0,
  meal_type    text default 'snack', -- 'breakfast','lunch','dinner','snack','pre','post'
  logged_at    timestamptz default now(),
  notes        text,
  created_at   timestamptz default now()
);

alter table public.meals enable row level security;
create policy "Users manage own meals" on meals for all using (auth.uid() = user_id);
create index idx_meals_user_date on meals(user_id, logged_at);

-- Workouts & Exercises
create table public.workout_sessions (
  id           uuid default gen_random_uuid() primary key,
  user_id      uuid references auth.users(id) on delete cascade not null,
  name         text not null,
  type         text default 'strength', -- 'strength','cardio','flexibility'
  duration_min int,
  calories_burned int,
  notes        text,
  logged_at    timestamptz default now(),
  created_at   timestamptz default now()
);

create table public.workout_exercises (
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
create policy "Users manage own sessions" on workout_sessions for all using (auth.uid() = user_id);
create policy "Users manage own exercises" on workout_exercises for all using (auth.uid() = user_id);
create index idx_sessions_user_date on workout_sessions(user_id, logged_at);

-- Body Metrics & Water
create table public.body_metrics (
  id            uuid default gen_random_uuid() primary key,
  user_id       uuid references auth.users(id) on delete cascade not null,
  weight_kg     numeric(5,1),
  body_fat_pct  numeric(4,1),
  muscle_mass_kg numeric(5,1),
  waist_cm      numeric(5,1),
  logged_at     timestamptz default now()
);

create table public.water_logs (
  id        uuid default gen_random_uuid() primary key,
  user_id   uuid references auth.users(id) on delete cascade not null,
  glasses   int default 1,
  logged_at timestamptz default now()
);

alter table public.body_metrics enable row level security;
alter table public.water_logs enable row level security;
create policy "Users manage own metrics" on body_metrics for all using (auth.uid() = user_id);
create policy "Users manage own water" on water_logs for all using (auth.uid() = user_id);

-- Auto-create profile on user registration
create policy "Users can insert own profile" on profiles for insert with check (auth.uid() = id);

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username, full_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1)),
    coalesce(new.raw_user_meta_data->>'full_name', '')
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
