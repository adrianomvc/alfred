#!/usr/bin/env python3
"""Stamp the model the host actually ran into a demand's `001-state.md`.

The toolbar shows the policy *target* marked `nao confirmado` whenever the state
carries no `model:` field. On the DEVIN CLI that target used to be a Claude model
name the host cannot even run. This reads what really ran from the host's own
records and records it, so the toolbar reports fact instead of intent.

Degrades (D3): a host with no readable source leaves the state untouched and says
so; the toolbar keeps its explicit `nao confirmado` marker.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.common import write_state_fields  # noqa: E402
from shared.observability.infrastructure.adapters.devin.session import (  # noqa: E402
    read_session_model,
)

READERS = {"devin-cli": read_session_model}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--host", "-Host", dest="host", default="devin-cli",
                        choices=sorted(READERS))
    parser.add_argument("--config-root", dest="config_root", default="",
                        help="host configuration root (defaults to the documented location)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state = Path(args.state_path).resolve()
    if not state.is_file():
        print(f"State nao encontrado: {state}")
        return 2

    found = READERS[args.host](args.config_root or None)
    if not found:
        print(f"Modelo do host {args.host} nao encontrado; state inalterado "
              "(toolbar mantem o alvo marcado como nao confirmado).")
        return 0

    label = found["uid"] or found["model"]
    if args.dry_run:
        print(f"Registraria model: {label} (fonte: {found['source']})")
        return 0

    write_state_fields(state, {"model": label, "host": args.host}, section="Progress")
    print(f"model: {label} registrado em {state.name} (fonte: {found['source']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
