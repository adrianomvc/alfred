# Version Adoption

Alfred uses one global installation at `~/.alfred` and always follows
`origin/main`. Demand stamps are an audit trail, not runtime pins.

## Contract
- Check `origin/main` at session start (boot) or via an explicit
  `alfred framework update`. Checkpoints never fetch or adopt: they only warn
  (from the cached `runtime/last-update-check.json`) when the installation has
  not been verified recently — adoption mid-demand stays a boot/explicit act.
- Finish the current atomic command before updating; never replace files during
  an in-flight helper operation.
- Validate the candidate in a temporary Git worktree before promotion.
- Promote only by fast-forward after the canonical framework gate passes.
- Active demands adopt the promoted version immediately. Record
  `old commit -> new commit` in state and audit.
- Never keep persistent version directories, tag pins, commit pins, or a
  demand-specific checkout.

Use `alfred framework status` to inspect installed and remote commits and
`alfred framework update --state <001-state.md>` to update and stamp an active
demand. Concurrent updates are serialized by a runtime lock.

## Honest Degradation
If Git, the network, or `origin/main` is unavailable, report `not verified` and
do not invent a version. If candidate validation or migration compatibility
fails, keep the current installation unchanged and block adoption. A local
framework without Git may still be used as Markdown, stamped `not-git`, but it
cannot claim to be current.

## Recovery
Rollback is a repository release action: fix or revert the faulty commit on
`main`, validate it, and run the updater again. Local rollback and pins are not
supported because they would make the single installation diverge from the
governing branch.
