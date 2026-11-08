# Observatories: the project observatory and the personal ones

**Status:** approved by the operator (2026-10-21). It is the basis of the roadmap everyone
works from. **For:** the Lens repos, Tapestry, Loom memory,
and anyone building an observatory from these parts.

## In one paragraph

There are two kinds of observatory. **The Lens, with all its modules, is the project
observatory.** There is one per project, run by the project's maintainer, and it is the larger,
shared view. It observes the knowledge exchanges between the project's contributors and agents
and builds a project knowledge map. **Personal observatories** are smaller. There is one per
contributor, it is private, and it follows that person across all their projects. Tapestry
and Loom memory plan to build them from elements of the Lens. The two meet only at a
project's shared interfaces.

Above both sits a third layer, added 2026-11-07: **QuickPrime, the shared knowledge graph.**
Many people, each with their own memory and observers over many projects, feed it the
telemetry they choose to share about what they are learning and building. Their private data
stays with them; the shared knowledge accumulates in one graph. See
[The shared knowledge graph](#the-shared-knowledge-graph-quickprime).

## The two observatories

```mermaid
flowchart TB
  subgraph PERSONAL["Personal observatories (Tapestry / Loom memory): one per contributor, private, span projects"]
    PA["A's personal observatory"]
    PB["B's personal observatory"]
  end
  subgraph LENS["The Lens = the project observatory (one per project, run by its maintainer)"]
    EX["Extraction<br/>(lens-ingest)"]
    DB["Curation dashboard<br/>review · library · graph"]
    OB["Exchange signals<br/>(lens-observe)"]
    WH["Workflow oversight<br/>(pluggable; models swappable)"]
    KM["Project knowledge map"]
  end
  LIB[("Lens modules<br/>(reusable elements)")]
  PA -->|supports| A["A's work on this project"]
  PB -->|supports| B["B's work on this project"]
  A <-->|knowledge exchange| B
  A --> DB
  B --> DB
  EX -->|candidates| DB
  WH -.->|watches health of| EX
  WH -.->|watches health of| DB
  OB -.->|observes exchanges in| DB
  OB -->|exchange telemetry| KM
  LIB -.->|elements reused to build| PERSONAL
  LENS -.->|built from| LIB
```

| | Project observatory (the Lens) | Personal observatory |
|---|---|---|
| How many | one per project | one per contributor |
| Run by | the project's maintainer | the contributor (built by Tapestry / Loom memory) |
| Observes | knowledge exchanges between contributors and agents at the project's shared interfaces | one person's work across all their projects |
| Produces | the project knowledge map and the verified project library | the contributor's evolving model of how they work |
| Privacy | shared within the project | private |
| Exists in PROVES? | yes (PROVES is one project's observatory) | no; it comes from the operator's architecture |

## Inside the project observatory

Each Lens module observes something different, for a different reader:

| Part | What it does or observes | For whom | Repo |
|---|---|---|---|
| Shared standard + launcher | the database shape every module meets on; stands up an observatory against an injected `LENS_DB_URL` | every module | lens-core |
| Extraction | agents capture candidates from the project's sources and feed the curation dashboard | contributors | lens-ingest |
| Review + promotion | humans accept, reject or edit candidates; accepted ones enter the library | contributors | lens-review |
| Library, graph, MCP read | people and agents use what has been verified | contributors, agents | lens-serve |
| Exchange signals | how knowledge moves between contributors: reviewer patterns, calibration, activity | the project | lens-observe |
| Workflow oversight | whether the machinery works: pipeline and intake health, errors, agent trust and proposals | the maintainer | new repo (proposed, name pending) |
| Access + tenancy | organizations, members, roles, sign-in, row security | every module | new repo (proposed, name pending) |

Workflow oversight is a **slot**, not a fixed team. It writes health, trust and proposal records
that the dashboard reads, and the standard names no model, so the agents that fill it can change
at any time.

## Lens elements a personal observatory could reuse

These are candidates for Tapestry and Loom memory to judge, not a design for them. Tapestry
decides what its personal observatory needs.

```mermaid
flowchart LR
  subgraph LENSMODS["Lens elements"]
    S["Shared standard<br/>candidates → decisions → verified + lineage"]
    L["Launcher<br/>injected connection"]
    I["Intake / extraction"]
    R["Review<br/>(human confirms)"]
    V["Read side<br/>(library + MCP)"]
    O["Signals over activity"]
    W["Oversight slot"]
  end
  subgraph PERS["A personal observatory"]
    P1["What the observer infers about how the person works"]
    P2["The person confirms or corrects it"]
    P3["Agents read the confirmed model"]
  end
  S --> P1
  L --> PERS
  I --> P1
  R --> P2
  V --> P3
  O --> P1
  W -.-> PERS
```

| Lens element | Possible use at personal scale |
|---|---|
| Shared standard (candidates → decisions → verified, with lineage) | inferences about the person stay candidates until the person confirms them, with a record of where each came from |
| Launcher with injected connection | a personal observatory is another instance, pointed at the person's own private database |
| Intake / extraction | capture from the person's own sources |
| Review | the person confirms, corrects or rejects what was inferred |
| Read side (library + MCP) | the person's agents read only the confirmed model |
| Signals over activity | activity signals across the person's projects |
| Oversight slot | watches the health of the personal observer's own agents |

**What this asks of every Lens module:**
- **Neutral about scale:** nothing assumes "one project" when it could be "one person".
- **Injected connection:** nothing hardcodes a backend.
- **Small interface:** each module's interface is only what it touches on the shared bus.

The Lens already follows these as reuse rules. Personal reuse is a further reason to keep them.

## The boundary between them

- A project observatory receives only what happens at the project's shared interfaces:
  contributions, reviews, explanations, handoffs.
- A personal observatory keeps everything else private. Taking part in a project does not
  expose a contributor's other projects or private context.
- Anything more that crosses from personal to project crosses because the contributor chose to
  send it.
- In the database, this is a rule on what crosses the bus (like row security), not a table.
  Where it is enforced is still open.

## The shared knowledge graph (QuickPrime)

The operator's decision (2026-11-07, loom memory
`decision-quickprime-is-the-shared-knowledge-graph-2026-11-07`): QuickPrime is the module where
many people's memories and observers connect to build one shared knowledge graph. Her example: a
group of friends, each with observers over many projects, feeding one shared graph. It is not a
game for now; the scope is the functionality.

```mermaid
flowchart TB
  QP[("QuickPrime: the shared knowledge graph<br/>many people, many projects")]
  subgraph ALICE["Member A (private)"]
    AM["A's own memory server"]
    AP["A's personal observatory"]
  end
  subgraph BOB["Member B (private)"]
    BM["B's own memory server"]
    BP["B's personal observatory"]
  end
  subgraph PROJ["A project both work on"]
    LP["The Lens: project observatory"]
  end
  AM -->|chosen shared telemetry| QP
  AP -->|chosen shared telemetry| QP
  BM -->|chosen shared telemetry| QP
  BP -->|chosen shared telemetry| QP
  LP -->|project knowledge it may share| QP
  AP -.->|works on| LP
  BP -.->|works on| LP
```

| | Personal observatory | Project observatory (the Lens) | Shared graph (QuickPrime) |
|---|---|---|---|
| How many | one per person | one per project | one, shared by many people |
| Holds | one person's private model and memory | one project's verified knowledge and map | what members choose to share about what they learn and build |
| Privacy | private | shared within the project | shared among members; nothing private enters |

- Each member builds their own memory server from QuickPrime's build-your-own instructions.
  Liz's own memory (Loom_MCP) is the reference implementation and is never exposed.
- The same boundary rule holds one layer up: only what a member or project deliberately sends
  crosses into the graph.
- How contributions connect, which telemetry is sent, how a contribution is checked before it
  counts, and privacy at that boundary are **QuickPrime's research items**, not decided here.
  The Lens spine (candidates → decisions → verified) is one option QuickPrime may evaluate.
- On the Lens side: a project observatory may contribute to the graph. What it sends waits on
  QuickPrime's contract (roadmap item `project-observatory-feeds-shared-graph`).

## Open

- Final names for the two proposed repos (workflow oversight; access + tenancy), after the
  full decomposition is reconciled.
- Which Lens elements Tapestry actually reuses, and whether they are shared as packages or
  copied. Tapestry is breaking itself down now, so this follows its plan.
- Where the personal-to-project boundary is enforced (in the standard, in each personal
  observatory, or both).

## Sources

- Surveyor module map, section 7: `Lizo-RoadTown/surveyor`,
  `docs/decomposition/proves/module-map.md`.
- Surveyor evaluation: `docs/decomposition/evaluations/2026-10-21-observation-layers.md`.
- The operator's description of individual and shared project layers, 2026-10-21.
- The operator's description of QuickPrime as the shared knowledge graph, 2026-11-07.
