---
type: process
module: lens-core
surfaces: [roadmap]
date: 2026-11-07T18:23
source_commits: {}
---

# lens-log installed globally (user scope) at 0.1.5

## What was done
- Found nine repos declaring a `decomposition.json` (AWG, education-lab, lens-core, lens-ingest,
  lens-review, lens-serve, lens-observe, QuickPrime, Surveyor). Only three had lens-log
  installed, each at a different version: lens-core 0.1.5, education-lab 0.1.4, Surveyor 0.1.2.
- Backed up `~/.claude/plugins/installed_plugins.json` to
  `installed_plugins.json.bak-2026-11-07-lens-log-global`.
- Updated the lizo-skills marketplace and ran `claude plugin install lens-log@lizo-skills
  --scope user`. User settings now enable it.
- Removed the three project-scope lens-log rows so older versions cannot shadow the global
  install. That earlier lesson is recorded in loom memory as
  `gotcha-plugin-case-duplicate-project-installs-shadow-updates-2026-08-22`.
- Roadmap item `install-lens-log-everywhere` is done.

## What was found / decided
A global install is safe: lens-log finds `decomposition.json` by walking up from the working
directory and does nothing where none exists. None exists in `C:\Users\Liz` or above. User scope
records no project path, so the c:/C: drive-letter trap does not apply. Cost: a short Python
start per file or shell tool call in every project. QuickPrime declares a `decomposition.json`,
so it is now enforced too. Open sessions pick up the hooks only after a restart. The old cache
folders 0.1.2 and 0.1.4 are unused and can be pruned.

## Lessons
A per-repo install for a tool that already no-ops outside its declared repos only adds
version drift.
