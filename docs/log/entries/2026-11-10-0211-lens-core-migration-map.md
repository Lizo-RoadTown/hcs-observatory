---
type: decision
module: lens-core
surfaces: [roadmap]
date: 2026-11-10T02:11
source_commits: {}
---

# lens-core migration map: becoming the observatory interface (proposed)

## What was done
Wrote `docs/plans/2026-11-10-lens-core-migration-map.md` against the operator's settled homes. It covers what leaves (H1 to H6, with conditions and order), what arrives (the web dashboard, the observatory console, the admin console slot, the UI package, the screens), the contracts (lens-core owns the settings model; it consumes QuickPrime B and C through the API only), conflicts and risks, order, and a proposed charter.

## What was found / decided
Nothing moves without the operator's approval. Key risks:
- lens-core changes from a Python package to a web-app repo;
- lens-core is public, so no data, service details or security findings go here;
- privacy defaults are interface requirements;
- the dashboard moves before or after the first closed loop, never during it.

The charter text is proposed, not applied.

## Lessons
none
