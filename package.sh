#!/usr/bin/env bash
# Packaging script for GitHub Release

VERSION="1.1.0"
OUTPUT_DIR="dist"
ARCHIVE_NAME="hybrid-agent-v$VERSION.tar.gz"

echo "📦 Đang đóng gói Hybrid Agent v$VERSION..."

mkdir -p $OUTPUT_DIR

# Tạo file nén bao gồm tất cả các file cần thiết, loại bỏ venv và logs
tar -czf "$OUTPUT_DIR/$ARCHIVE_NAME" \
    --exclude="venv" \
    --exclude="logs" \
    --exclude=".git" \
    --exclude="dist" \
    --exclude="__pycache__" \
    --exclude="*.log" \
    .

echo "✅ Đóng gói hoàn tất: $OUTPUT_DIR/$ARCHIVE_NAME"
echo "Kích thước: $(du -sh $OUTPUT_DIR/$ARCHIVE_NAME | cut -f1)"