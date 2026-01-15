begin;
create extension if not exists "pgcrypto";
create table if not exists public.signals (
  id uuid primary key default gen_random_uuid(),

  asset text not null,
  market text not null,
  timeframe text not null,
  session text,

  trade_direction text not null
    check (trade_direction in ('BUY', 'SELL')),

  entry_min numeric(12,5),
  entry_max numeric(12,5),
  take_profit numeric(12,5),
  stop_loss numeric(12,5),

  target_pips integer,
  risk_reward numeric(6,2),

  confidence numeric(5,2)
    check (confidence >= 0 and confidence <= 100),

  trade_type text default 'intraday',

  engine_version text default 'quantix-core',
  source text default 'AI',

  expires_at timestamptz,
  created_at timestamptz default now(),

  is_active boolean default true
);
create table if not exists public.signal_snapshots (
  id uuid primary key default gen_random_uuid(),

  signal_id uuid
    references public.signals(id)
    on delete cascade,

  snapshot jsonb not null,
  created_at timestamptz default now()
);
create table if not exists public.telegram_dispatch_log (
  id uuid primary key default gen_random_uuid(),

  signal_id uuid
    references public.signals(id)
    on delete cascade,

  telegram_chat_id text not null,
  sent_at timestamptz default now(),

  unique (signal_id, telegram_chat_id)
);
create index if not exists idx_signals_asset_tf
on public.signals(asset, timeframe);

create index if not exists idx_signals_confidence
on public.signals(confidence desc);

create index if not exists idx_signals_active
on public.signals(is_active);
alter table public.signals enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where policyname = 'public_read_signals'
  ) then
    create policy "public_read_signals"
    on public.signals
    for select
    using (true);
  end if;
end $$;
commit;
