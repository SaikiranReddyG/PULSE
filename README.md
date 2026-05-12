# See Everything. Respond Faster.

**PULSE turns security events from all your local tools into one unified, live dashboard.**

---

## The Problem

Your security team is running multiple detection tools—network monitoring, attack labs, system audits—but they're working in silos. Security events scatter across different outputs, making it hard to spot patterns, respond quickly, or even know what's happening right now. You need visibility, not a spreadsheet of disconnected alerts.

---

## What It Does

### 🔄 One Place for All Events
PULSE collects security events from your network monitors, attack labs, and system monitors in real-time. No more juggling separate terminals. They all flow into a single, searchable database.

### 📊 Live Event Dashboard
A terminal-native TUI shows what's happening now. Drill into specific incidents without leaving the command line. Tabs organize events by source. Refresh is instant.

### 🚨 Instant Alerts (Optional)
High and critical events trigger Discord notifications. Alert your team the moment something matters.

### 📦 Lightweight. Single-Host.
No distributed infrastructure to manage. Runs on one Linux box. Simple architecture means simple troubleshooting.

---

## Who It's For

- **Security defenders** running multiple open-source security tools locally who need a command center
- **Red teamers and attack sim ops** who want to correlate defensive signals during lab work
- **DevOps / sys admins** using network IDS, system monitors, or attack frameworks who need real-time visibility

---

## Get Started

PULSE works in three steps:

1. **Receive** — Launch the PULSE stack on a Linux box (receiver, database, streaming)
2. **Connect** — Point your security tools to the PULSE event endpoint
3. **View** — Open the live dashboard and start seeing events in real-time

---

## License

[See LICENSE file](./LICENSE)

---

**Ready to see your security events in one place?** [Set it up now.](#get-started)
