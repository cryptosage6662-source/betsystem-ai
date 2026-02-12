# Hostinger Quick Install - Copy & Paste Setup

**Server:** srv1354333.hstgr.cloud  
**User:** root  
**Time:** ~5 minutes

---

## STEP 1: Access Your Server

### Via Hostinger Web Terminal (Easiest)
1. Go to **https://hpanel.hostinger.com/**
2. Login
3. **Products → Your VPS → Console/Terminal**
4. A web terminal opens

### Via Termius (iPhone/iPad)
1. Open Termius
2. Add new: `srv1354333.hstgr.cloud`, user `root`, use password from Hostinger email
3. Connect

---

## STEP 2: Paste This Command (Creates Workspace)

Copy entire block and paste into terminal:

```bash
cd /root && mkdir -p polymarket_trading && cd polymarket_trading && python3 << 'INIT'
import json
with open('positions.json', 'w') as f:
    json.dump({'positions': [], 'cash': 100.0, 'equity': 100.0, 'high_water': 100.0, 'max_drawdown': 0.0, 'consecutive_losses': 0}, f, indent=2)
with open('trades.json', 'w') as f:
    json.dump([], f, indent=2)
with open('equity_live.json', 'w') as f:
    json.dump([], f, indent=2)
print('✅ Workspace ready!')
INIT
```

**Expected output:** `✅ Workspace ready!`

---

## STEP 3: Create polymarket_live.py

### Option A: Using File Upload (Easiest for Most)
1. Download these 3 files from your local machine:
   - `polymarket_live.py`
   - `dashboard.py`
   - (optional) `polymarket_api.py`

2. In Hostinger Web Terminal, run:
   ```bash
   cd /root/polymarket_trading
   ls -la
   ```

3. If you see **File Manager** option in Hostinger dashboard:
   - Upload the 3 files directly to `/root/polymarket_trading/`
   - Skip to Step 4

### Option B: Copy-Paste from Text (If Upload Doesn't Work)

**Get the file from your local directory:**
```bash
cat /data/.openclaw/workspace/CREATE_POLYMARKET_LIVE.txt
```

Copy the **entire content** starting from `cat > /root/polymarket_trading/polymarket_live.py << 'ENDFILE'` to the end.

Paste into Hostinger terminal and hit Enter.

---

## STEP 4: Create dashboard.py

Same as Step 3, but for:
```bash
cat /data/.openclaw/workspace/CREATE_DASHBOARD.txt
```

Copy entire content, paste into Hostinger terminal.

---

## STEP 5: Test Installation

In Hostinger terminal:

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

✅ If you see this = **Trading engine works!**

---

## STEP 6: Test Dashboard

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

✅ If you see this = **Dashboard works!**

---

## STEP 7: Set Up Cron (Auto 15-Minute Trading)

```bash
# Edit crontab
crontab -e
```

If prompted for editor, choose **nano** (press `1` or `2`)

Paste this line at the bottom:
```
*/15 * * * * cd /root/polymarket_trading && python3 polymarket_live.py >> trading.log 2>&1
```

Save:
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

Verify it was saved:
```bash
crontab -l
```

You should see the line you added.

---

## STEP 8: Verify Cron Is Running

Check logs after 15 minutes:

```bash
cd /root/polymarket_trading
tail -20 trading.log
```

You'll see something like:
```
🚀 Polymarket Live Trading System - Phase 4
Bankroll: $100.00, Position Size: 0.30%
...
✅ Cycle completed successfully
```

✅ If you see this = **Cron works!**

---

## STEP 9: Monitor From Termius (iPhone/iPad)

Open Termius anytime to check:

```bash
cd /root/polymarket_trading

# View live dashboard
python3 dashboard.py

# View recent logs
tail -20 trading.log

# View positions (live)
cat positions.json
```

---

## ✅ Success Checklist

- [ ] Workspace created (`/root/polymarket_trading/`)
- [ ] polymarket_live.py uploaded
- [ ] dashboard.py uploaded
- [ ] First cycle runs without errors
- [ ] Dashboard displays correctly
- [ ] Cron job set up
- [ ] Cron running every 15 minutes (check logs)
- [ ] Can access from Termius

Once all checked = **System is live!**

---

## 🆘 Troubleshooting

### "Command not found: python3"
```bash
apt update && apt install python3 -y
```

### "Permission denied"
```bash
chmod +x /root/polymarket_trading/*.py
```

### Cron not running
```bash
# Check if cron is running
systemctl status cron

# If not, start it
systemctl start cron
```

### Can't see trading.log
- Cron hasn't run yet (waits 15 min from setup)
- Or markets API is down temporarily
- Both are OK - system will keep trying

### Files won't upload via File Manager
- Use copy-paste method (Option B)
- Or use SCP from your computer:
```bash
scp /data/.openclaw/workspace/polymarket_live.py root@srv1354333.hstgr.cloud:/root/polymarket_trading/
```

---

## 📞 Next Steps

1. **Let it run for 7 days** — cron handles everything automatically
2. **Check dashboard daily** — `python3 dashboard.py`
3. **After 7 days** — review performance, proceed to Phase 5

You're done! System is now live on Hostinger. 🚀

