#!/usr/bin/env python3
"""
Cron Scheduler for Polymarket Live Trading
Runs the trading cycle every 15 minutes
"""

import subprocess
import json
import os
from datetime import datetime

LIVE_SCRIPT = "/data/.openclaw/workspace/polymarket_live.py"
LOG_FILE = "/data/.openclaw/workspace/trading_log.jsonl"

def run_trading_cycle():
    """Execute trading cycle and log results"""
    try:
        result = subprocess.run(
            ["python3", LIVE_SCRIPT],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": result.returncode == 0,
            "stdout": result.stdout[:500],  # First 500 chars
            "stderr": result.stderr[:200] if result.stderr else None,
        }
        
        # Append to JSONL log
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        if result.returncode == 0:
            print(f"✅ Trading cycle completed: {datetime.now()}")
        else:
            print(f"❌ Trading cycle failed: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": "Timeout (>60s)",
        }
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"❌ Trading cycle timeout")
    
    except Exception as e:
        print(f"❌ Error running trading cycle: {e}")

if __name__ == "__main__":
    run_trading_cycle()
