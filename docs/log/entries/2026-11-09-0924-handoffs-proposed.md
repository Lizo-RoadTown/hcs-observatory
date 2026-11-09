---
type: decision
module: lens-core
surfaces: [roadmap]
date: 2026-11-09T09:24
source_commits: {}
---

# lens-core hand-offs proposed under the six-module target

## What was done
Wrote `docs/plans/2026-11-09-lens-core-handoffs.md`: seven hand-offs (H1 to H7), each with its files, receiver and condition to move. Answered education-lab's questions on the gate intake (Tapestry's architecture-registry `POST /candidates`, migration 007) and on attention settings (none exist).

## What was found / decided
- **To QuickPrime:** the spine and its tests, and the launcher.
- **To Tapestry:** the roadmap and its CI, and the log index.
- **To the engine:** the oversight tables.
- **To Surveyor:** the module list and ids.
- **To the interface home:** the architecture docs.

Each hand-off moves only after the receiver accepts; tests must pass on the receiving side before lens-core drops its copy. Whether lens-core is archived afterward is the operator's call.

## Lessons
none
