#!/bin/bash
# Restart web dashboard on Hostinger

echo "🌐 Restarting BetSystem Web Dashboard..."
echo ""

# Kill any existing process
pkill -f "web_dashboard" || echo "No existing process"

# Sleep briefly
sleep 2

# Restart dashboard
cd /root/polymarket_trading

# Run in background
nohup python3 web_dashboard.py > dashboard.log 2>&1 &

echo "✅ Dashboard restarted"
echo "📊 Access at: http://srv1354333.hstgr.cloud:8000"
echo "📝 Log file: dashboard.log"
echo ""
echo "To monitor:"
echo "  tail -f dashboard.log"
