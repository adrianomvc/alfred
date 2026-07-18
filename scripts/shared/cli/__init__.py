"""Canonical services for the Alfred command-line helper."""


def run(argv=None):
    """Load the CLI dispatcher lazily so domain services stay independently importable."""
    from shared.cli.parser import run as dispatch

    return dispatch(argv)


__all__ = ["run"]
