-- Database schema for question-bank-generator

create table if not exists questions (
  id text primary key,                    -- "{source_site}:{source_id}"
  title text not null,
  source_site text not null,              -- codeforces | cses | geeksforgeeks | leetcode | hackerrank
  source_url text not null,
  source_id text not null,
  category text,
  difficulty text,
  companies text[] default '{}',
  problem_statement text,
  examples jsonb,
  constraints jsonb,
  test_cases jsonb,                       -- each: {input, expected_output, edge_case_type, origin}
  solution_python text,
  solution_java text,
  verified boolean default false,
  python_verified boolean default false,
  java_verified boolean default false,
  partial_scrape boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists questions_source_site_idx on questions (source_site);
create index if not exists questions_category_idx on questions (category);
create index if not exists questions_difficulty_idx on questions (difficulty);
create index if not exists questions_verified_idx on questions (verified);
create index if not exists questions_companies_idx on questions using gin (companies);

create table if not exists pipeline_runs (
  id bigserial primary key,
  started_at timestamptz default now(),
  finished_at timestamptz,
  new_questions int default 0,
  failed_sources text[] default '{}',
  status text                              -- running | success | partial | failed
);
