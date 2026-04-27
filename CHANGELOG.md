# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-04-27

### ✨ New Features
- **Web Dashboard** (9router-style): Real-time monitoring, provider config, live logs, terminal interface
- **GUI Installer** (`installer_gui.py`): One-click installation for non-technical users
- **Systemd Service** (`setup-systemd.sh`): Auto-start on boot, automatic restart on crash
- **GitHub Release Packaging** (`package.sh`): Automated release builds
- **API Endpoints**: `/api/stats`, `/api/config`, `/health` for dashboard integration
- **Terminal Interface**: Web-based terminal to send requests directly from dashboard

### 🔧 Improvements
- Enhanced error handling and logging
- Configuration management via web UI
- Status monitoring (online/offline detection)
- Uptime tracking
- Recent sessions display

### 📦 Packaging
- Automated release builds (20KB tar.gz)
- Systemd service file generation
- Virtual environment management

---

## [1.0.0] - 2026-04-27

### Added
- Initial release of **Hybrid Agent AI Provider**.
- OpenAI-compatible API server (`/v1/chat/completions`).
- Local tool execution engine (Terminal, File I/O).
- 1-click installation and startup scripts (`install.sh`, `start.sh`).
- Comprehensive testing suite (`test.sh`).
- Support for OpenClaw Zero Token integration.
- Built-in Mock Reasoning for standalone provider mode.
- Persistent session state management using SQLite.
- Automatic recovery cron job monitor.
