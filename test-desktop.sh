#!/bin/bash
# Quick test script to verify the desktop app works in development mode

echo "========================================="
echo "Question Paper Generator - Dev Test"
echo "========================================="
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found. Run 'npm install' first."
    exit 1
fi

echo "✓ Node modules installed"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check Django installation
if ! python3 -c "import django" 2>/dev/null; then
    echo "❌ Django not installed. Install requirements: pip install -r requirements.txt"
    exit 1
fi

echo "✓ Django installed"

# Check database
if [ ! -f "db.sqlite3" ]; then
    echo "⚠ Database not found. Running migrations..."
    python3 manage.py migrate --noinput
fi

echo "✓ Database ready"

echo ""
echo "========================================="
echo "Starting desktop application..."
echo "========================================="
echo ""
echo "The app will:"
echo "  1. Show a loading screen"
echo "  2. Start Django server automatically"
echo "  3. Load the web interface"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start in development mode
npm run dev
