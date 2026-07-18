-- Suggest to Aureon — a lightweight, globally-accessible contribution
-- feature (not a journey stage). Students can suggest a missing career,
-- opportunity, or resource; request a feature; report incorrect/outdated
-- information; or leave general feedback. Every submission starts
-- 'pending' and is never auto-published into the trusted knowledge base —
-- a human reviews it via the reviewer-secret-gated endpoints in
-- api/v1/suggestions.py before status can move to 'approved'/'implemented'.
--
-- context_type/context_id/context_metadata is one flexible jsonb-backed
-- attachment point (e.g. context_type='career', context_id=<career id>,
-- context_metadata={'page_or_feature': 'Career Explorer'}) instead of six
-- separate mostly-null columns (related_career_id, related_opportunity_id,
-- related_resource_name, page_or_feature, country, additional_context) —
-- deliberately not over-normalized.

create table if not exists suggestions (
    id text primary key,
    student_id text not null,
    category text not null,
    title text not null,
    description text not null,
    source_url text,
    context_type text,
    context_id text,
    context_metadata jsonb not null default '{}',
    status text not null default 'pending',
    review_notes text,
    reviewed_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists suggestions_student_id_idx on suggestions (student_id);
create index if not exists suggestions_status_idx on suggestions (status);
create index if not exists suggestions_category_idx on suggestions (category);
