---
type: process
module: lens-core
surfaces: [roadmap]
date: 2026-11-08T12:16
source_commits: {}
---

# Checked QuickPrime's project-feed proposal against the spine: two issues

## What was done
Read QuickPrime's round-2 proposal (QuickPrime ba433f7,
`docs/proposals/2026-11-08-hook-in-contract-round-2.md`, sections 2 and 3). Checked the
project-observatory feed against standard 0.2.0 and lens-observe's boundary for roadmap item
`project-observatory-feeds-shared-graph`. Sent the findings to QuickPrime.

## What was found / decided
- **Fits:**
  - verified entries cross as candidates in the graph's scope, with lineage in sources (the
    spine's crossing path);
  - kinds per lab;
  - person-shaped types excluded;
  - contributor ids carried, never minted.
- **Issue 1: activity.signal and exchange.event are signals, not candidates.** Tapestry's adopted
  language standard says "signal = evidence, never a proposal … signals ≠ candidates"
  (`tapestry/docs/plans/2026-10-21-master-plan-personal-loop.md:112`). They need a store
  beside the spine.
- **Issue 2: the exchange-event shape and signal names belong to lens-observe and the pl-001
  decision.** lens-observe has not derived its plan (`lens-observe/CHARTER.md:11` names only the
  signals), and `observe-signal-vocabulary` is open.
- The roadmap item stays loose.

## Lessons
Check a cross-module proposal against the shared language rules (signal vs candidate), not only
against the schema: the schema would have accepted signals as candidates.
