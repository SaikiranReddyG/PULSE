"""Entry point for the codex-dashboard console script."""

import sys
from pathlib import Path

from codex_dashboard.app import CodexDashboardApp


def _default_db_path() -> str:
    """Find the codex SQLite database.

    Check (in order):
    1. CODEX_DB environment variable
    2. ./sqlite/codex.db relative to cwd
    3. ~/codex-workspace/codex-platform/sqlite/codex.db

    Returns the first path found.
    """
    import os

    # Check environment variable
    if env_path := os.getenv("CODEX_DB"):
        return env_path

    # Check relative to cwd
    cwd = Path.cwd()
    if (cwd / "sqlite" / "codex.db").exists():
        return str(cwd / "sqlite" / "codex.db")

    # Check default workspace location
    return str(Path.home() / "codex-workspace" / "codex-platform" / "sqlite" / "codex.db")


def main() -> int:
    db_path = _default_db_path()
    app = CodexDashboardApp(db_path=db_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
