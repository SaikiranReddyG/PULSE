"""Entry point for the codex-dashboard console script."""

import sys
from pathlib import Path

from codex_dashboard.app import CodexDashboardApp


def _default_db_path() -> str:
    """Find the codex SQLite database.

    Resolution order:
    1. CODEX_DB env var
    2. ./sqlite/codex.db (run from codex-platform repo root)
    3. ../sqlite/codex.db (run from dashboard/ subdirectory)
    """
    import os

    env = os.environ.get("CODEX_DB")
    if env:
        return env

    cwd = Path.cwd()
    for candidate in [cwd / "sqlite" / "codex.db",
                      cwd.parent / "sqlite" / "codex.db"]:
        if candidate.is_file():
            return str(candidate)

    # Fall back to the most likely path; the app will display an error if missing.
    return str(cwd / "sqlite" / "codex.db")


def main() -> int:
    db_path = _default_db_path()
    app = CodexDashboardApp(db_path=db_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
