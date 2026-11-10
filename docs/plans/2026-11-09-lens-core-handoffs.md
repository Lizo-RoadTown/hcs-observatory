# Proposal: lens-core's hand-offs under the six-module target (2026-11-09)

**Status:** proposal. Each hand-off happens only after the receiving module accepts it.
**Basis:** target `docs/architecture/target-architecture.md`; implementation map
`surveyor/docs/decomposition/2026-11-09-implementation-map.md`, section 7 ("What dissolves").
**Update 2026-11-10:** the operator settled the homes (loom memory
`decision-module-homes-and-operator-answers-2026-11-10`). lens-core becomes the **observatory
interface**, so it keeps its architecture docs and continues after these hand-offs.

| # | Piece | Files | To | Condition to move |
|---|---|---|---|---|
| H1 | The spine (standard 0.2.0) and its tests | `docs/schema/spine.sql`, `tests/test_spine.py`, `tests/conftest.py` (guarded DB fixture) | **QuickPrime** | **Accepted** (QuickPrime PR #1, standard 0.3.0 without oversight); merged per the operator 2026-11-10. lens-core removes its copy once that merge is confirmed on QuickPrime main. |
| H2 | The launcher and its packaging | `src/lens_core/launch.py`, `tests/test_launch.py`, the wheel config in `pyproject.toml` | **QuickPrime** | **Accepted** with H1 (renamed `quickprime new`). |
| H3 | The roadmap, its checker and CI | `roadmap.yaml`, `ROADMAP.md`, `scripts/roadmap.py`, `tests/test_roadmap.py`, and only the roadmap-check step of `.github/workflows/roadmap.yml` (the spine and launcher tests go with H1/H2) | **Tapestry** | **Accepted.** It lands after H6, because `roadmap.py` checks owners against the module list. Tapestry re-owns the items. |
| H4 | The log index | `scripts/log_index.py`, `tests/test_log_index.py`, `.github/workflows/log-index.yml`, `docs/log/INDEX.md` | **Surveyor** | **Operator decision 2026-11-10:** Surveyor owns structural consistency checks; the adaptive engine consumes relevant findings. Publishing the index is a separate access decision; private entries are never published automatically. It lands after H6, and needs a read token for the private repos. |
| H5 | The oversight tables | the `oversight_*` part of `spine.sql` | **Adaptive engine: education-lab** (settled 2026-11-10) | the engine design takes agent trust |
| H6 | The module list and ids | the whole-system part of `decomposition.json`: `modules`, `proposed`, `ids`, `retired_ids` | **Surveyor** | Surveyor takes it first, since H3 and H4 depend on it. lens-core keeps a piece-level `decomposition.json` (`role`, `sources`, `surfaces`) for its own lens-log. `pr-` ids stay stable; pr-002 to pr-007 retire or re-map to the six modules. |
| H7 | Architecture docs | `docs/architecture/target-architecture.md`, `observatories.md` | **Stay in lens-core** | lens-core is the observatory interface (settled 2026-11-10) |
| H8 | Scope research and the lens-core log | `docs/plans/*`, `docs/log/entries/*` | stay in lens-core | lens-core continues as the interface; it does not retire |

## How each move is done
- **Copy with history where it helps** (git filter-repo, as for Surveyor's founding).
  Otherwise copy files and cite the lens-core commit.
- **Both sides record a decision log entry:** the sender records the hand-off, the receiver
  records the acceptance.
- **Tests and CI move with the code and must pass on the receiving side** before lens-core
  removes its copy.
- **Order:** H6 and H3/H4 first (they unblock coordination), then H1/H2 with QuickPrime round 3,
  then H5 with the engine design. H7 no longer moves.

## Open
- Retirement of the four Lens sibling repos (all stubs), following the same evaluation.
