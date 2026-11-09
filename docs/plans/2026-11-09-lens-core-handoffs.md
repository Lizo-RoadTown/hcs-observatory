# Proposal: lens-core's hand-offs under the six-module target (2026-11-09)

**Status:** proposal. Each hand-off happens only after the receiving module accepts it.
**Basis:** target `docs/architecture/target-architecture.md`; implementation map
`surveyor/docs/decomposition/2026-11-09-implementation-map.md`, section 7 ("What dissolves").
Under the map, lens-core has no remaining role once these are done.

| # | Piece | Files | To | Condition to move |
|---|---|---|---|---|
| H1 | The spine (standard 0.2.0) and its tests | `docs/schema/spine.sql`, `tests/test_spine.py`, `tests/conftest.py` (guarded DB fixture) | **QuickPrime** | QuickPrime accepts it as the graph's store. The **oversight tables** (`oversight_*`) stay out of QuickPrime and go to the adaptive engine (H5). |
| H2 | The launcher and its packaging | `src/lens_core/launch.py`, `tests/test_launch.py`, the wheel config in `pyproject.toml` | **QuickPrime** | goes with H1 (it provisions a graph instance) |
| H3 | The roadmap, its checker and CI | `roadmap.yaml`, `ROADMAP.md`, `scripts/roadmap.py`, `tests/test_roadmap.py`, `.github/workflows/roadmap.yml` | **Tapestry** | Tapestry accepts. Items are re-owned to the six modules first. |
| H4 | The log index | `scripts/log_index.py`, `tests/test_log_index.py`, `.github/workflows/log-index.yml`, `docs/log/INDEX.md` | **Tapestry** | Tapestry accepts. The list of repos it reads is updated to the modules that log. |
| H5 | The oversight tables | the `oversight_*` part of `spine.sql` | **Adaptive engine** (provisional starter: education-lab) | the engine design takes agent trust |
| H6 | The module list and ids | `decomposition.json` (`modules`, `proposed`, `ids`, `retired_ids`) | **Surveyor** | Surveyor takes it. `pr-` ids stay stable; pr-002 to pr-005 and pr-007 retire or re-map as the modules dissolve. |
| H7 | Architecture docs | `docs/architecture/target-architecture.md`, `observatories.md` | **Observatory interface** home (open) | once the operator names the home; until then they stay here as the reference |
| H8 | Scope research and the lens-core log | `docs/plans/*`, `docs/log/entries/*` | stay in lens-core's history | archived when lens-core retires |

## How each move is done
- **Copy with history where it helps** (git filter-repo, as for Surveyor's founding).
  Otherwise copy files and cite the lens-core commit.
- **Both sides record a decision log entry:** the sender records the hand-off, the receiver
  records the acceptance.
- **Tests and CI move with the code and must pass on the receiving side** before lens-core
  removes its copy.
- **Order:** H6 and H3/H4 first (they unblock coordination), then H1/H2 with QuickPrime round 3,
  then H5 with the engine design, and H7 last.

## Open
- Whether lens-core is archived or kept as a pointer repo after H1 to H7 (operator).
- Retirement of the four Lens sibling repos (all stubs), following the same evaluation.
