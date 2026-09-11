-- Supabase (Postgres) schema for the Mafia Certificate redeem-code system.
-- Run this in the Supabase SQL editor before importing data.

create table if not exists codes (
    id bigint generated always as identity primary key,
    code text not null unique,
    type text not null,       -- money | cmoney | item | background | setvariable | setdf | setbg | setam | setm | join
    variable text,            -- name of the Ren'Py variable this code affects
    screen text,              -- screen/item variable name (item, background, setam)
    amount numeric,           -- money/item amount
    value jsonb,               -- arbitrary value for setdf / setbg
    active boolean not null default true,
    created_at timestamptz not null default now()
);

create index if not exists codes_code_idx on codes (code);
