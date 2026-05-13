"""Entry point for the pulse-dashboard console script."""

import os
import sys
from pathlib import Path

from pulse_dashboard.app import PulseDashboardApp


def _default_db_path() -> str:
    env = os.environ.get("PULSE_DB")
    if env:
        return env
    cwd = Path.cwd()
    for candidate in [cwd / "sqlite" / "pulse.db", cwd.parent / "sqlite" / "pulse.db"]:
        if candidate.is_file():
            return str(candidate)
    return str(cwd / "sqlite" / "pulse.db")


def main() -> int:
    db_path = _default_db_path()
    app = PulseDashboardApp(db_path=db_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
