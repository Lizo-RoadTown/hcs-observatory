---
type: decision
module: lens-core
surfaces: [architecture]
date: 2026-11-09T02:14
source_commits: {}
---

# Agreed target architecture: five components, recorded

## What was done
Wrote `docs/architecture/target-architecture.md` from the operator's agreed text and chart (chart validated), with a section on what exists today versus the target (from Surveyor evaluation 4). Marked `observatories.md` as superseded in part. Recorded in loom memory as `decision-target-architecture-five-components-2026-11-09`.

## What was found / decided
- **Loom_MCP** is working memory, with separate personal and team instances.
- **QuickPrime** is the project's verified knowledge graph, with no personal equivalent.
- **The combined Lens and education-lab repo** holds the observatory interface, the adaptive engine and the domain packages.
- **Surveyor** is structure.
- **Tapestry** is coordination and execution.

The observatory's settings govern the engine, and Tapestry enforces the authority to act. Domain and scope are separate. The doc moves to the combined repo once it is named.

## Lessons
none
