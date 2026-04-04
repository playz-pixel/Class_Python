#!/bin/bash
# setup.sh — Cài đặt Auto Homework Solver

echo ""
echo "  ╔══════════════════════════════╗"
echo "  ║   AUTO HOMEWORK SOLVER       ║"
echo "  ║   Thiết lập môi trường       ║"
echo "  ╚══════════════════════════════╝"
echo ""

# Kiểm tra Python
if ! command -v python3 &>/dev/null; then
    echo "  ✗  Python 3 chưa được cài. Tải tại: python.org"
    exit 1
fi
PY=$(python3 --version)
echo "  ✓  $PY"

# Cài requests
echo "  →  Cài thư viện requests..."
pip install requests -q
echo "  ✓  requests đã sẵn sàng"

# Tạo .env mẫu nếu chưa có
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Auto Homework Solver — Cấu hình
GEMINI_API_KEY=
GITHUB_TOKEN=
GITHUB_USER=
GITHUB_REPO=
GITHUB_BRANCH=main
OUTPUT_FOLDER=baitap
EOF
    echo "  ✓  Tạo file .env (điền API keys vào)"
else
    echo "  ✓  File .env đã tồn tại"
fi

echo ""
echo "  Chạy chương trình:"
echo "      python3 main.py"
echo ""
