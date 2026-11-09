---
type: decision
module: lens-core
surfaces: [architecture]
date: 2026-11-09T01:14
source_commits: {}
---

# Architecture: personal and shared Memory are the same shape at two scales

## What was done
Added the operator's framing and a chart to the shared-graph section of
`docs/architecture/observatories.md`. Her words are in loom memory as
`decision-personal-and-shared-memory-same-shape-2026-11-09`.

## What was found / decided
A person's Memory (Loom_MCP is the reference) and the team's shared Memory (QuickPrime) are the
same shape at different scales, serving different audiences. Only what concerns the shared
project flows up. How much code the two share, and what the shared scale adds (review, links,
one copy of a fact), is research for Loom_MCP, QuickPrime and Tapestry.

## Lessons
lens-core first overstated this as "the same module installed at team scope". The operator meant
the shape. Record the operator's claim at the level of precision she gives it.
