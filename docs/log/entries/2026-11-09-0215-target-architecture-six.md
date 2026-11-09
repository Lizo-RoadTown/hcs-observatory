---
type: decision
module: lens-core
surfaces: [architecture]
date: 2026-11-09T02:15
source_commits: {}
---

# Target architecture corrected: six components

## What was done
Replaced the component table in `docs/architecture/target-architecture.md` with the operator's corrected list.

## What was found / decided
The adaptive engine with its domains, and the observatory interface, are separate components, making six:
- Loom_MCP (memory);
- QuickPrime (verified graph);
- the adaptive engine plus domains;
- the observatory interface;
- Surveyor;
- Tapestry.

Open: whether the engine and the interface share one repo, and the name.

## Lessons
Record the operator's table exactly as she gives it; a later message may split a row.
