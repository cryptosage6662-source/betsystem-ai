#!/bin/bash

# BetSystem AI - Quick Start Script
# Run locally first, then deploy to Railway

echo "🚀 BetSystem AI - Quick Start"
echo "=============================="
echo ""

# Check Python
echo "1️⃣ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install Python 3.8+"
    exit 1
fi
echo "✅ Python $(python3 --version)"
echo ""

# Install dependencies
echo "2️⃣ Installing dependencies..."
pip install -q fastapi uvicorn pydantic sqlalchemy python-dotenv 2>/dev/null || \
pip install --user -q fastapi uvicorn pydantic sqlalchemy python-dotenv 2>/dev/null || \
echo "⚠️  Note: Some packages might need manual install"
echo ""

# Create .env if not exists
if [ ! -f .env ]; then
    echo "3️⃣ Creating .env file..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
DEBUG=False
DATABASE_URL=sqlite:///./betsystem.db
SECRET_KEY=dev-secret-key-change-in-production
EOF
    echo "✅ Created .env (update for production)"
fi
echo ""

# Test imports
echo "4️⃣ Testing Python imports..."
python3 << 'PYEOF'
try:
    import fastapi
    import uvicorn
    import pydantic
    import sqlalchemy
    print("✅ All imports successful")
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("   Run: pip install -r requirements.txt")
PYEOF
echo ""

# Start backend
echo "5️⃣ Starting FastAPI backend..."
echo "   Starting on http://localhost:8000"
echo "   API Docs at http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""

python3 -m uvicorn betsystem_api:app --host 0.0.0.0 --port 8000 --reload
