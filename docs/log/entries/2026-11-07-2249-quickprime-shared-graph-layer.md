---
type: decision
module: lens-core
surfaces: [architecture, roadmap, source]
date: 2026-11-07T22:49
source_commits:
  PROVES_LIBRARY: 02ab37e
---

# Architecture: QuickPrime is the shared knowledge graph above the observatories

## What was done
- `docs/architecture/observatories.md` gains a third layer from the operator's 2026-11-07
  decision (loom memory `decision-quickprime-is-the-shared-knowledge-graph-2026-11-07`):
  - a summary paragraph, a section with a validated chart, and a three-column comparison
    (personal, project, shared graph);
  - the boundary rule extended one layer up;
  - the "Open" list updated (final names after reconciliation).
- New loose roadmap item `project-observatory-feeds-shared-graph` (owner lens-core, consumer
  quickprime), waiting on QuickPrime's contract.
- To explain the PROVES key to the operator, listed which PROVES programs read Supabase key
  variables (names only, no values): `SUPABASE_SERVICE_ROLE_KEY` is read 12 times, including
  `extraction-api/worker.py` and `production/worker/extraction_worker.py`; the dashboard uses
  `VITE_SUPABASE_ANON_KEY`.

## What was found / decided
QuickPrime's design questions (telemetry, hook-in contract, verification, privacy) are
QuickPrime's research items, per the operator's correction the same day. lens-core records only
the layer and its own side: a project observatory may contribute once the contract exists. The
Lens spine is named as one option QuickPrime may evaluate, not a prescription.

## Lessons
When a new layer appears above an approved architecture, record it in the same document, with the
same boundary rule, rather than starting a parallel description.
