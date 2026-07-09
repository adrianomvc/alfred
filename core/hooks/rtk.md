# RTK Hook

RTK is a local terminal tool plus shell hook that keeps command output bounded.
It supports Alfred's terminal token policy; it is not a source of truth and not
a framework dependency.

## Supported host
Automatic RTK setup is currently scoped to **DEVIN CLI** installs only. Other
hosts may use RTK manually, but Alfred must not require it there.

## Install inputs
- RTK binary/package source: provided by the organization, currently expected
  from Artifactory.
- Installer variable/flag:
  - PowerShell: `install.ps1 -RtkUrl <artifact-url>`
  - bash: `ALFRED_RTK_URL=<artifact-url> bash install/install.sh`
- Skip flag:
  - PowerShell: `-SkipRtk`
  - bash: `ALFRED_SKIP_RTK=1`

No URL means no download. The installer records that RTK setup was skipped and
Alfred falls back to `rules/common/terminal-token-policy.md`.

## Setup
1. Resolve the installed `rtk` command from `PATH`; if absent and an approved
   artifact URL was provided, install it into the user's local tool directory.
2. Run `rtk init -g` for DEVIN CLI user-level terminal hooks.
3. In a project that needs local hook state, run `rtk init` from the repo root.
4. Verify with `rtk --version`.

## Use
When RTK is available, prefer bounded commands through RTK:
- `rtk cat`
- `rtk grep`
- `rtk diff`
- `rtk test`

Still inspect summaries first (`git diff --stat`, targeted searches, limited
logs). RTK reduces terminal noise; it does not replace judgment.

## Degradation
If RTK cannot be installed or initialized, use bounded native commands and
record the limitation only when it affects validation, evidence, or a human
decision.
