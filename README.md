# hcs-observatory (the observatory)

**Status:** being rebuilt. The observatory is the **interface** of a six-module system: where
a person or team sees what the system observes, reviews findings, proposals and knowledge,
and controls how the system behaves. Its identity and boundary are in
[`CHARTER.md`](CHARTER.md).

| Module | Repo | What it does |
|---|---|---|
| memory | `hcs-memory` | recording, retrieval, recall and search, personal and team |
| project knowledge graph | `hcs-project-knowledge-graph` | admission, review and verified project knowledge |
| adaptive engine | `hcs-adaptive-engine` | watches authorized evidence, finds friction, proposes improvements |
| **observatory** | `hcs-observatory` (here) | visualization, review, settings and controls |
| decomposition | `hcs-decomposition` | structure, responsibilities, interfaces, the base-module standard |
| coordination | `hcs-coordination` | connects components, equips agents, executes approved changes |

The architecture is in [`docs/architecture/target-architecture.md`](docs/architecture/target-architecture.md).
The migration plan is in [`docs/plans/2026-11-10-lens-core-migration-map.md`](docs/plans/2026-11-10-lens-core-migration-map.md).

## Now
There is no runnable code here yet. The earlier Lens database standard and launcher moved out
on 2026-11-10:
- to the project knowledge graph (standard 0.3.0);
- to the adaptive engine (the trust tables).

Next comes the interface itself:
1. the web dashboard and observatory console arrive from coordination;
2. the review screens are built against the project knowledge graph's contracts;
3. the settings model.

It is built to the base-module standard 0.2 (hcs-decomposition).

## Rules
- **The observatory owns no data store.** It reads and sends only through the owning
  modules' contracts.
- **This repo is public.** No user data, live-service details, keys or security findings.

Formerly `lens-core`, the main repo of "The Lens", decomposed from the PROVES reference system.
That history is precedent, not identity.

Apache-2.0.
