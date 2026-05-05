"""Color palette and theme constants. All color values used by the app
should come from here. Do not hardcode hex values in widgets."""

# Base palette (minimal, dark)
BG = "#1a1a1a"
SURFACE = "#222222"
BORDER = "#333333"
TEXT = "#e8e8e8"
TEXT_MUTED = "#888888"
ACCENT = "#5fafd7"  # calm blue, used for headers, selections, links

# Severity ladder — these are the only "color-as-meaning" assignments
SEVERITY_INFO = "#888888"       # gray
SEVERITY_LOW = "#5fafd7"        # calm blue
SEVERITY_MEDIUM = "#d7af5f"     # warm yellow
SEVERITY_HIGH = "#d77a5f"       # orange
SEVERITY_CRITICAL = "#d75f5f"   # red

SEVERITY_COLOR = {
    "info": SEVERITY_INFO,
    "low": SEVERITY_LOW,
    "medium": SEVERITY_MEDIUM,
    "high": SEVERITY_HIGH,
    "critical": SEVERITY_CRITICAL,
}

# Source colors (for the source-breakdown bar — neutral, distinct)
SOURCE_COLOR = {
    "syswatch": "#5fafaf",    # teal
    "sentinel": "#af87d7",    # muted purple
    "netlab": "#87af5f",      # muted green
}
