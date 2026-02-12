# Hostinger Deployment Guide

**Server:** srv1354333.hstgr.cloud  
**User:** root  
**Workspace:** /root/polymarket_trading

---

## STEP 1: Connect to Your Server

### Option A: Via Hostinger Web Terminal
1. Go to **Hostinger Dashboard → Products → Your VPS → Manage**
2. Click **"Console"** or **"Terminal"** button
3. You'll get a web-based terminal access

### Option B: Via SSH (Termius on iPhone/iPad)
1. Open **Termius**
2. Add new host:
   - **Hostname:** srv1354333.hstgr.cloud
   - **Port:** 22
   - **Username:** root
   - **Password:** (from Hostinger email) or SSH key
3. Connect

---

## STEP 2: Create Workspace & Initialize

**Run these commands on your Hostinger server:**

```bash
# Create directories
mkdir -p /root/polymarket_trading
mkdir -p /root/polymarket_trading/backtest_results
mkdir -p /root/polymarket_trading/memory

# Enter workspace
cd /root/polymarket_trading

# Initialize data files
python3 << 'EOF'
import json

# positions.json
with open('positions.json', 'w') as f:
    json.dump({
        'positions': [],
        'cash': 100.0,
        'equity': 100.0,
        'high_water': 100.0,
        'max_drawdown': 0.0,
        'consecutive_losses': 0
    }, f, indent=2)

# trades.json
with open('trades.json', 'w') as f:
    json.dump([], f, indent=2)

# equity_live.json
with open('equity_live.json', 'w') as f:
    json.dump([], f, indent=2)

print('✅ Data files created')
EOF
```

---

## STEP 3: Upload Trading Files

You need to upload these files to `/root/polymarket_trading/`:

1. **polymarket_live.py** - Main trading engine
2. **dashboard.py** - Monitoring dashboard
3. **cron_scheduler.py** - Automation wrapper
4. **polymarket_api.py** (optional) - API helper
5. **polymarket_strategy.py** (optional) - Strategy helper

### Method A: Using Hostinger File Manager
1. Hostinger Dashboard → File Manager
2. Navigate to `/root/polymarket_trading/`
3. Upload files

### Method B: Using SCP (if SSH works)
```bash
# From your local machine
scp ~/polymarket_live.py root@srv1354333.hstgr.cloud:/root/polymarket_trading/
scp ~/dashboard.py root@srv1354333.hstgr.cloud:/root/polymarket_trading/
scp ~/cron_scheduler.py root@srv1354333.hstgr.cloud:/root/polymarket_trading/
```

### Method C: Copy/Paste via Web Terminal
1. Open file in text editor on local machine
2. Copy entire content
3. On Hostinger terminal:
   ```bash
   cat > /root/polymarket_trading/polymarket_live.py << 'EOF'
   # PASTE FILE CONTENT HERE
   EOF
   ```

---

## STEP 4: Test First Cycle

**On Hostinger server:**

```bash
cd /root/polymarket_trading
python3 polymarket_live.py
```

**Expected output:**
```
🚀 Polymarket Live Trading System - Phase 4
Bankroll: $100.00, Position Size: 0.30%
============================================================
Trading Cycle: 2026-02-12 HH:MM:SS
============================================================
No crypto markets found. Skipping cycle.
✅ Cycle completed successfully
```

---

## STEP 5: Test Dashboard

```bash
cd /root/polymarket_trading
python3 dashboard.py
```

**Expected output:**
```
======================================================================
               POLYMARKET PAPER TRADING DASHBOARD
======================================================================

📊 PORTFOLIO STATUS
  Bankroll:              $100.00
  Current Equity:        $100.00
  P&L:                   $0.00 (0.00%)
  ...
```

---

## STEP 6: Set Up Cron Job (Auto 15-minute cycles)

**On Hostinger server:**

```bash
# Edit crontab
crontab -e

# Add this line (runs every 15 minutes):
*/15 * * * * cd /root/polymarket_trading && python3 polymarket_live.py >> trading.log 2>&1

# Save (Ctrl+X, then Y, then Enter if using nano)
```

**Verify cron is set:**
```bash
crontab -l
```

---

## STEP 7: Monitor Logs

**View trading log:**
```bash
cd /root/polymarket_trading
tail -f trading.log
```

**View positions (live):**
```bash
cat positions.json | python3 -m json.tool
```

**View trades:**
```bash
cat trades.json | python3 -m json.tool
```

---

## STEP 8: Access Dashboard from iPhone (Termius)

1. **Open Termius** on your phone
2. **Connect** to srv1354333.hstgr.cloud (root)
3. **Run dashboard:**
   ```bash
   cd /root/polymarket_trading && python3 dashboard.py
   ```
4. **Refresh when needed:** exit (Ctrl+C), run again

---

## Troubleshooting

### "Command not found: python3"
```bash
# Install Python
apt update && apt install python3 -y
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x /root/polymarket_trading/*.py
```

### "No module named json"
- json is built-in, this shouldn't happen
- Try: `python3 --version`

### Cron not running
```bash
# Check if cron service is running
service cron status

# Start if needed
service cron start
```

### Can't connect via Termius
- Verify SSH port is 22 in Hostinger settings
- Check if firewall allows port 22
- Try password auth instead of SSH key

---

## Maintenance

**Daily:**
```bash
python3 dashboard.py
```

**Check logs:**
```bash
tail -20 trading.log
```

**Restart cron (if needed):**
```bash
service cron restart
```

---

## Files Location
- **Workspace:** `/root/polymarket_trading/`
- **Trading script:** `/root/polymarket_trading/polymarket_live.py`
- **Dashboard:** `/root/polymarket_trading/dashboard.py`
- **Logs:** `/root/polymarket_trading/trading.log`
- **Data:** `/root/polymarket_trading/positions.json`, `trades.json`, `equity_live.json`

---

## Success Checklist

- ✅ Workspace created
- ✅ Data files initialized
- ✅ Trading files uploaded
- ✅ First cycle runs without errors
- ✅ Dashboard displays correctly
- ✅ Cron job set up
- ✅ Can access via Termius from iPhone

Once all checked, system is ready for 7-day validation!
