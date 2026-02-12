#!/bin/bash
# Polymarket Trading System - Hostinger Setup
# Run this on your Hostinger server via terminal/SSH

set -e

WORKSPACE="/root/polymarket_trading"

echo "🚀 Setting up Polymarket Trading System on Hostinger..."
echo ""

# 1. Create workspace
echo "📁 Creating workspace directory..."
mkdir -p $WORKSPACE
mkdir -p $WORKSPACE/backtest_results
mkdir -p $WORKSPACE/memory

# 2. Initialize data files
echo "📝 Initializing data files..."
cd $WORKSPACE

python3 << 'INIT'
import json
import os

# Initialize positions
with open('positions.json', 'w') as f:
    json.dump({
        'positions': [],
        'cash': 100.0,
        'equity': 100.0,
        'high_water': 100.0,
        'max_drawdown': 0.0,
        'consecutive_losses': 0
    }, f, indent=2)

# Initialize trades
with open('trades.json', 'w') as f:
    json.dump([], f, indent=2)

# Initialize equity history
with open('equity_live.json', 'w') as f:
    json.dump([], f, indent=2)

print('✅ Data files created')
INIT

# 3. Show workspace location
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Upload trading files to: $WORKSPACE"
echo "2. Run: cd $WORKSPACE && python3 polymarket_live.py"
echo "3. Set up cron job for 15-minute cycles"
echo ""
echo "Dashboard: python3 dashboard.py"
