---
type: process
module: lens-core
surfaces: [roadmap]
date: 2026-11-10T02:02
source_commits: {}
---

# Correction: QuickPrime PR #1 is open, not merged; H5 before dropping the spine

## What was done
Corrected the H1 row of `docs/plans/2026-11-09-lens-core-handoffs.md`.

## What was found / decided
The earlier update said H1 was merged per the operator. GitHub shows QuickPrime PRs #1 to #4 all OPEN (2026-11-10). The operator's "the merges are done" referred to education-lab, whose PRs #20 to #25 are merged. QuickPrime caught the error.

Ordering, also from QuickPrime: the oversight tables exist only in lens-core's 0.2.0 `spine.sql`. So the order is QuickPrime PR #1 merged, then H5 moves the oversight tables to education-lab, then lens-core drops its copy.

## Lessons
When the operator says "the merges are done", check which PRs are merged on GitHub before recording it against a specific PR.
