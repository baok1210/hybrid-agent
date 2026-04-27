# 🤖 Hybrid Agent AI Provider (v2.0.0)

**Hybrid Agent** is an OpenAI-compatible API provider designed for "Invisible Computing". It leverages **OpenClaw's zero-token reasoning** (via Web UI) combined with **local tool execution** (Terminal, File I/O) to provide a powerful, free, and autonomous AI agent experience.

---

## ✨ Key Features (New in v2.0.0)

- 🌐 **Web Dashboard**: 9router-style interface at `http://localhost:8001/dashboard`.
- 📦 **One-Click Installer**: GUI-based setup (`installer_gui.py`) for non-technical users.
- ⚙️ **Systemd Service**: Auto-start on boot and auto-restart on crash (`setup-systemd.sh`).
- 🛠️ **Local Tools**: Terminal execution, File Read/Write, and Directory Listing.
- 🧠 **Smart Orchestration**: "Think-Do" pattern for autonomous task solving.
- 🔒 **Secure**: Bearer Token authentication and command blacklisting.
- 📊 **Monitoring**: Real-time logs, metrics, and session history.

---

## 🚀 Quick Start (For Newbies)

### 1. Download & Install
The easiest way to get started is using the **GUI Installer**:
```bash
git clone https://github.com/baok1210/hybrid-agent.git
cd hybrid-agent
python3 installer_gui.py
```
*Click the **Install** button and wait for the "✅ Installed" status.*

### 2. Access the Dashboard
Once installed, click **Start Server** in the GUI or run `./start.sh`, then visit:
👉 **[http://localhost:8001/dashboard](http://localhost:8001/dashboard)**

### 3. Connect to Your Tools
Copy your API credentials from the dashboard and paste them into **Clawx**, **Hermes**, **Cursor**, or any OpenAI-compatible client:
- **Base URL**: `http://localhost:8001/v1`
- **API Key**: `hybrid-free-key-2026`
- **Model**: `hybrid-agent`

---

## 🛠 Advanced Setup (For Power Users)

### Run as a System Service (Linux)
To make the agent run automatically in the background on every boot:
```bash
sudo ./setup-systemd.sh
```

### Manual CLI Commands
- **Install**: `./install.sh`
- **Start**: `./start.sh` (Runs in background, logs to `logs/server.log`)
- **Stop**: `./stop.sh`
- **Test**: `./test.sh`

---

## 🔄 How It Works

1. **Think**: Requests are routed to **OpenClaw** (or Mock mode) for high-level reasoning.
2. **Do**: The agent uses **Local Tools** to execute terminal commands or manage files.
3. **Observe**: Results are fed back into the reasoning loop until the goal is achieved.
4. **Respond**: The final result is returned in standard OpenAI JSON format.

---

## ⚙️ Configuration
Configuration is managed via `config.yaml` or directly through the **Web Dashboard > Providers** tab.

```yaml
api:
  port: 8001
  auth_token: "hybrid-free-key-2026"
openclaw:
  url: "http://localhost:18789/v1/chat/completions"
```

---

## 📦 Releases
Download the latest pre-packaged release from the [Releases](https://github.com/baok1210/hybrid-agent/releases) page:
`hybrid-agent-v2.0.0.tar.gz` (Automated build via `package.sh`)

---

## 🤝 Support & Contribution
- **Author**: Bảo DV 💵
- **GitHub**: [baok1210/hybrid-agent](https://github.com/baok1210/hybrid-agent)
- **Email**: baok1210@gmail.com

---
*MIT License © 2026 Hybrid Agent Project*
