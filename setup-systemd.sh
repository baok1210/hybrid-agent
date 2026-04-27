#!/usr/bin/env bash
# Setup Systemd Service for Hybrid Agent

if [[ $EUID -ne 0 ]]; then
   echo "❌ Vui lòng chạy bằng sudo: sudo ./setup-systemd.sh"
   exit 1
fi

PROJECT_DIR="/home/bun/hybrid-agent"
USER_NAME="bun"

echo "⚙️  Đang tạo service file..."

cat <<EOF > /etc/systemd/system/hybrid-agent.service
[Unit]
Description=Hybrid Agent AI Provider
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn hybrid-agent.api_server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_DIR/logs/server.log
StandardError=append:$PROJECT_DIR/logs/server.log

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd..."
systemctl daemon-reload
systemctl enable hybrid-agent
systemctl start hybrid-agent

echo "✅ Đã kích hoạt Hybrid Agent service!"
echo "Kiểm tra trạng thái: systemctl status hybrid-agent"