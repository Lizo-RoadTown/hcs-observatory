---
type: decision
module: lens-core
surfaces: [roadmap]
date: 2026-11-10T01:59
source_commits: {}
---

# Hand-off plan updated: settled homes; log index to Surveyor

## What was done
Updated `docs/plans/2026-11-09-lens-core-handoffs.md` for the operator's 2026-11-10 decisions (loom memory `decision-module-homes-and-operator-answers-2026-11-10`, `decision-log-index-to-surveyor-publishing-separate-2026-11-10`).

## What was found / decided
- H1 and H2 are accepted by QuickPrime.
- H3 (roadmap) is accepted by Tapestry, after H6.
- H4 (log index) goes to Surveyor by function. Publishing it is a separate access decision, and private entries are never published automatically.
- H5 goes to education-lab.
- H6 goes first; lens-core keeps a piece-level `decomposition.json` for its own lens-log.
- H7 stays: lens-core is the observatory interface and does not retire.

## Lessons
none
