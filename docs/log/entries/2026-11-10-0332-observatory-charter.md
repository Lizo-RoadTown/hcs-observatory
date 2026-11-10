---
type: decision
module: lens-core
surfaces: [identity]
date: 2026-11-10T03:32
source_commits: {}
---

# Charter: lens-core becomes the observatory (approved)

## What was done
Replaced CHARTER.md with the observatory charter the operator approved on 2026-11-10 (loom memory `decision-charters-and-pkg-license-approved-2026-11-10`; text from the migration map, section 6). Updated CLAUDE.md to match:
- who the repo is;
- the contract rule, replacing the bus rule;
- the coordination install URL.

## What was found / decided
lens-core's identity is now the observatory interface. It owns the interface apps and the settings model, and holds no data store. The frozen spine and launcher stay only until H5.

## Lessons
none
