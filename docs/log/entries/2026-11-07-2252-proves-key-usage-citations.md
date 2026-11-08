---
type: process
module: lens-core
surfaces: [source]
date: 2026-11-07T22:52
source_commits:
  PROVES_LIBRARY: 02ab37e
  proves-curation-dashboard: c484e52
---

# PROVES key usage cited; dashboard hardcodes its anon key

## What was done
To back the key-replacement explanation with citations (read-only):
- `production/worker/extraction_worker.py:82` reads `SUPABASE_SERVICE_ROLE_KEY`;
- `extraction-api/worker.py:22` documents it as required;
- the dashboard reads its key at `proves-curation-dashboard/src/lib/supabase.ts:6`.

## What was found / decided
`src/lib/supabase.ts:6` hardcodes the project's public anon key as a fallback in a public repo.
Anon keys are meant to be public, but combined with tables that had row security off, they were
an exposure. The operator's key-replacement steps (new publishable and secret keys, then
deactivate the legacy anon and service_role keys) cover it. The grep printed the anon value into
this session; it is not repeated in any file.

## Lessons
Grepping config lines prints values. Print names only (`grep -o` on the variable name) when a
line may hold a key.
