---
type: decision
module: lens-core
surfaces: [architecture]
date: 2026-11-09T02:18
source_commits: {}
---

# Target architecture: six modules (operator's final version)

## What was done
Replaced `docs/architecture/target-architecture.md` with the operator's six-module text, chart (validated), repo directions, controls and loop example. The implementation map is in surveyor `docs/decomposition/2026-11-09-implementation-map.md`.

## What was found / decided
The six modules: working memory (Loom_MCP), verified project knowledge (QuickPrime), the adaptive engine plus domains, the observatory interface, decomposition (Surveyor), and coordination and execution (Tapestry). Each setting is enforced by the module that owns it. Under the map, lens-core dissolves after its hand-offs.

## Lessons
none
