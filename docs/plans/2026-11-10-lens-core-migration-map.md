# lens-core migration map: becoming the observatory interface (2026-11-10)

**Status:** proposed. Every move needs the operator's approval.
**Basis:**
- the operator's decision on module homes (loom memory
  `decision-module-homes-and-operator-answers-2026-11-10`);
- the target `docs/architecture/target-architecture.md`;
- the other modules' maps: Tapestry PR #206, QuickPrime PR #4, education-lab PR #26, Surveyor
  `docs/decomposition/2026-11-10-h6-h4-proposal.md`.

lens-core becomes the **observatory interface**: visualization, exploration, customization,
review and controls across the system, for both personal and project scopes. It keeps id
**pr-001**.

## 1. What leaves lens-core

| Piece | To | Condition and order |
|---|---|---|
| Spine (lens-core 0.2.0 → QuickPrime standard 0.3.0, without oversight), launcher, their tests and wheel config | QuickPrime (H1, H2) | QuickPrime PR #1 merged (it is **open**), then H5, then lens-core drops its copy |
| `bus` field and the `bus` surface in `decomposition.json` | **dropped, not moved** | in the same commit that drops `spine.sql`. Under the settled homes the spine is QuickPrime's private store, read only through contracts B and C, so it is no longer a shared bus. QuickPrime tracks schema changes through its own `standard` surface |
| Oversight tables (`oversight_*`) | education-lab (H5) | after QuickPrime PR #1; before lens-core drops `spine.sql` |
| Roadmap, its checker, test and CI step | Tapestry (H3) | after H6; lens-core's CI keeps running the tests that stay until they move |
| Log index, its test and workflow | Surveyor (H4) | after H6; adapted per Surveyor's proposal (nested role for education-lab; QuickPrime and Loom_MCP declarations) |
| Whole-system module list and ids | Surveyor (H6) | first. lens-core then flips its `decomposition.json` to a piece (role, sources, surfaces) **in the same commit** that removes the roadmap and log-index files (Surveyor's step 4) |

## 2. What arrives in lens-core

| Piece | From | Live state | Notes |
|---|---|---|---|
| Web dashboard: candidates promote, hold, reject; Grafana | **the-loom** `apps/web-dashboard` (the live copy, Vercel project `the-loom`; corrected 2026-11-10 per Tapestry) and tapestry `apps/web-dashboard` (not deployed) | live from the-loom's copy | First diff the two copies and pick the canonical one (the live one is the-loom's). Move that copy to lens-core, then repoint the `the-loom` Vercel project's source, which keeps the domain and env vars. Retire the other copy. **Not during the first closed loop**, which uses its approve button (Tapestry conflict 1) |
| Observatory console | tapestry `apps/docs-site` `/observatory` | live on Vercel | Splits a live site: one `/observatory` redirect from the docs site, coordinated with Tapestry |
| Admin console slot | tapestry `apps/admin-console` | empty slot | becomes the settings and controls area |
| UI package | tapestry `packages/ui` | slot | shared components |
| Review, library and graph screens | lens-review and lens-serve charters; PROVES dashboard (reference only) | design only | built against QuickPrime's contracts B and C |
| CLI `observatory` link | tapestry `packages/cli` | live | stays in Tapestry and points at the interface's URL |

## 3. Contracts

**lens-core owns: the settings model.** A versioned, per-scope settings document covering:
- attention;
- adaptation;
- authority;
- access;
- knowledge review.

Tapestry drafted the format as provisional starter, and education-lab proposed fields (cooldown,
arbiter, retention). lens-core takes ownership. Each setting is routed to the module that
enforces it:
- **the engine:**
  - attention: watch, cadence, depth, notify;
  - adaptation: enabled domains, thresholds, skill creation (proposal-only), acceptance check
    required, cooldown days, the arbiter;
- **Tapestry's executor:** authority and execution, defaulting to approval required;
- **Loom_MCP and QuickPrime:** access to their data, including retention days on stored signals.

Open: whether retention also covers the engine's own state. If it does, the settings model must
say so; the engine will honour it.

**lens-core consumes, never bypasses:**
- **QuickPrime B (graph reads) and C (review decisions):** through QuickPrime's API under
  lens-core's own role, **never the database** (QuickPrime conflict 2). The review actor comes
  from the user's token.
- **Loom_MCP:** inspect and manage memory, through its read API. A personal scope shows only
  that person's memory. The personal learner profile lives in Loom_MCP as the person's own
  memory section. lens-core shows it and lets the person correct it, and **holds no copy**. The
  engine reads it only under a scoped credential, which Loom_MCP has yet to design.
- **The engine:** findings and proposals, read; attention and adaptation settings, sent.
- **Tapestry:** status, approvals and execution settings. Approvals carry the approver from the
  token.
- **Surveyor:** structure, for exploring.
- **Telemetry:** read through Tapestry (Grafana today).

## 4. Conflicts and risks

1. **Language change.** lens-core is a Python package today (`lens_core`, launcher). The
   interface pieces are a Next.js app (dashboard) and an Astro site (console). After H1 and H2,
   lens-core becomes a web-app repo. Its CI and packaging are replaced, not extended.
2. **Public repo.** lens-core is public. Interface code is fine; **no user data, live service
   details, keys or security findings ever go here.** Settings and data live in the owning
   modules. Check the log entries before the move for anything sensitive.
3. **Privacy by design** (proposal review section 5):
   - team views show aggregates by default, with a minimum group size;
   - no individual friction view for others without the person's consent;
   - a self-view of what is collected about each person.

   These are interface requirements, not settings.
4. **Timing.** Move the dashboard either before the first closed loop (the review plan's P3,
   not Loom_MCP's P3 repoint) starts or after it
   finishes, never during it.
5. **Two Vercel deployments.** The dashboard and console stay separate deploys after the move
   unless the operator wants them merged. Merging is a later choice, not part of the move.

## 5. Order

1. **(Others)** H6 (Surveyor), then H3 (Tapestry), then H4 (Surveyor).
2. **lens-core:** one commit that flips its `decomposition.json` to a piece and removes the
   roadmap and log-index files. It keeps the spine and launcher test job of `roadmap.yml`
   (lens-core's only test CI) until step 3 drops them, so the spine never runs without CI.
3. **After QuickPrime PR #1 merges:** H5 (oversight to education-lab), then lens-core drops the
   spine, launcher and their tests, plus the `bus` field and surface, in one commit.
4. **After the settings contract (P0 item 3) is accepted:** build the settings and controls area.
5. **Before or after the first closed loop, not during:** diff the two dashboard copies, move
   the canonical one (Vercel `the-loom` source repoint), then the
   console (with the redirect).
6. **Then:** the review, library and graph screens against QuickPrime's B and C; memory
   inspect; the structure view.
7. **Adopt base-module standard 0.2** (operator-approved; hcs-decomposition d6de99e,
   `docs/reference/base-module-standard.md`) as part of becoming a web app:
   - declare `kinds: ["interface"]`, `instances: "multiple"` and a `layout` mapping for the
     web-app folders (open item 7.1, which lens-core proposes);
   - add `tests/accessibility/`, `tests/interaction/`, `tests/privacy/` (aggregates, a personal
     scope sees only its own person, no scope crossing) and the isolation test across personal
     and project scopes;
   - add `examples/embedded/`: a host mounts the views and supplies its own data clients.

## 6. Proposed charter (for the operator's approval; not applied)

> **Who you are.** lens-core is the **observatory interface** of the system: the place where a
> person or team sees what the system observes, inspects findings, proposals and knowledge, and
> controls how the system behaves.
>
> **Your core directive.** Present, explore and control.
> - **Visualize** telemetry, memory, verified knowledge, structure, findings and proposals.
> - **Let people review and approve:** knowledge contributions (QuickPrime) and improvement
>   proposals (Tapestry).
> - **Hold and route the settings:** attention, adaptation, authority, access and knowledge
>   review, each to the module that enforces it.
>
> **You are NOT** the memory, the knowledge graph, the adaptive engine, decomposition, or the
> executor. You read and send through their contracts. You never touch their databases
> directly, and you never act on projects yourself.
>
> **Your boundary.**
> - You own: the interface apps, the settings model and its routing.
> - You do not own any data store.
>
> **Scope and privacy.** Personal and project scopes are separate. A person's private data is
> visible only to that person. Team views are aggregate by default. Sharing the implementation
> never shares data.
>
> **Precedent is not identity.** Your history (the Lens lab and the PROVES decomposition) is
> precedent. This charter is your identity.
