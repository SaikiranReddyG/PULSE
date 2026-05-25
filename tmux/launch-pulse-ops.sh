#!/usr/bin/env bash
# Launches or attaches to the pulse-ops tmux session.
# Safe to call multiple times — only creates the session once.

SESSION="pulse-ops"
PLATFORM_DIR="/home/reddy/codex-workspace/codex-platform"

# If session already exists, attach and exit
if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux attach-session -t "$SESSION"
    exit 0
fi

# Window 0: dashboard (full screen)
tmux new-session -d -s "$SESSION" -n "dashboard" -x 220 -y 50
tmux set-option -g automatic-rename off
tmux set-option -g allow-rename off
tmux send-keys -t "$SESSION:0" "cd $PLATFORM_DIR && make dashboard" Enter

# Window 1: all logs side by side
tmux new-window -t "$SESSION:1" -n "logs"
tmux send-keys -t "$SESSION:1" "journalctl -fu pulse-syswatch" Enter
tmux split-window -h -t "$SESSION:1"
tmux send-keys -t "$SESSION:1.1" "journalctl -fu pulse-sentinel" Enter

# Window 2: syswatch only
tmux new-window -t "$SESSION:2" -n "syswatch"
tmux send-keys -t "$SESSION:2" "journalctl -fu pulse-syswatch" Enter

# Window 3: sentinel only
tmux new-window -t "$SESSION:3" -n "sentinel"
tmux send-keys -t "$SESSION:3" "journalctl -fu pulse-sentinel" Enter

# Window 4: free shell for manual commands (netlab etc)
tmux new-window -t "$SESSION:4" -n "shell"
tmux send-keys -t "$SESSION:4" "cd $PLATFORM_DIR" Enter

# Start on dashboard
tmux select-window -t "$SESSION:0"

# Attach
tmux attach-session -t "$SESSION"
