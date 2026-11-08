---
type: decision
module: lens-core
surfaces: [bus, roadmap]
date: 2026-11-07T22:02
source_commits: {}
---

# Review and promotion contract: verified entries trace to an accept decision by foreign key

## What was done
Roadmap item `review-promotion-contract`, revised from the reviewer's findings (R1, approved by
the operator):
- `decisions` gets `UNIQUE (id, candidate_id, action)`.
- `verified` gets `candidate_id` and `decision_id` (both NOT NULL) and `decision_action`
  (default and CHECK `'accept'`), with a composite foreign key to
  `decisions (id, candidate_id, action)`. The database now guarantees that every verified
  entry came from an accept decision on its own candidate. No triggers are used.
- The schema states the limits it cannot enforce without triggers: the candidate's status
  being 'accepted', and the accept being the latest decision. Those are the writer's job
  (lens-review).
- No unique `canonical_key`: the scope column (loose) will change what unique means.
- Database contract tests:
  - source to candidate to accept decision to verified succeeds and joins back to the source;
  - a verified entry with no decision fails;
  - promoting a reject fails;
  - borrowing another candidate's accept fails.
  The relationships test now creates its verified rows through the contract.
- The roadmap item's outcome is reworded to constraints only.

## What was found / decided
Two of the three PROVES defects the item once named are not lens-core work. The review_decision
CHECK conflict cannot occur (no such column), and the hardcoded `dashboard_user` is UI code
(lens-review) whose real fix is identity (access + tenancy, pr-007). The SQL promotion breakage
after migration 011 cannot recur, because the standard holds no promotion functions. Imports get
no exception: requiring the trace keeps one path into the library.

## Lessons
Without triggers, "this decision was an accept" can still be enforced by pinning a constant
column into a composite foreign key. State plainly what remains unenforced.
