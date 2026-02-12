#!/usr/bin/env python3
import json, os, statistics
from flask import Flask, render_template_string, jsonify
from datetime import datetime

app = Flask(__name__)
POSITION_FILE = "/data/.openclaw/workspace/positions.json"
TRADES_FILE = "/data/.openclaw/workspace/trades.json"
EQUITY_FILE = "/data/.openclaw/workspace/equity_live.json"

def load_positions():
    try:
        with open(POSITION_FILE) as f:
            return json.load(f)
    except:
        return {"positions": [], "count": 0}

def load_trades():
    try:
        with open(TRADES_FILE) as f:
            return json.load(f)
    except:
        return {"trades": [], "metrics": {}}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Polymarket Trading Dashboard</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #00d4ff; margin-bottom: 30px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #2a2a2a; border: 1px solid #00d4ff; padding: 20px; border-radius: 8px; }
        .card h3 { margin-top: 0; color: #00d4ff; }
        .value { font-size: 28px; font-weight: bold; margin: 10px 0; }
        .positive { color: #00ff00; }
        .negative { color: #ff4444; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #444; }
        th { background: #333; color: #00d4ff; font-weight: bold; }
        tr:hover { background: #333; }
        .status { padding: 8px 12px; border-radius: 4px; font-weight: bold; }
        .active { background: #004d00; color: #00ff00; }
        .inactive { background: #4d0000; color: #ff4444; }
        .circuit-breaker { background: #ffaa00; color: #000; padding: 8px 12px; border-radius: 4px; font-weight: bold; }
        .refresh { color: #888; font-size: 12px; }
    </style>
    <script>
        setInterval(() => location.reload(), 5000);
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Polymarket Trading Dashboard</h1>
        <div class="refresh">Auto-refreshing every 5 seconds...</div>
        
        <div class="metrics">
            <div class="card">
                <h3>💰 Total Trades</h3>
                <div class="value">{{ trades.count }}</div>
            </div>
            <div class="card">
                <h3>📊 Win Rate</h3>
                <div class="value {{ 'positive' if metrics.win_rate > 0 else 'negative' }}">
                    {{ "%.1f%%"|format(metrics.win_rate * 100) }}
                </div>
            </div>
            <div class="card">
                <h3>💵 Total P&L</h3>
                <div class="value {{ 'positive' if metrics.total_pnl >= 0 else 'negative' }}">
                    ${{ "%.2f"|format(metrics.total_pnl) }}
                </div>
            </div>
            <div class="card">
                <h3>📈 Positions</h3>
                <div class="value">{{ positions.count }}</div>
            </div>
        </div>

        <div class="card">
            <h3>⚙️ System Status</h3>
            <p>
                <strong>Cron Status:</strong> <span class="status active">✅ ACTIVE</span><br>
                <strong>Next Cycle:</strong> in ~5 min<br>
                <strong>Circuit Breaker:</strong> 
                {% if circuit_active %}
                    <span class="circuit-breaker">🛑 TRIGGERED (3 losses)</span>
                {% else %}
                    <span class="status active">✅ OK</span>
                {% endif %}
            </p>
        </div>

        <h3>📋 Recent Trades</h3>
        <table>
            <tr>
                <th>Market</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>Quantity</th>
                <th>P&L</th>
                <th>Status</th>
                <th>Time</th>
            </tr>
            {% for trade in trades.trades[:10] %}
            <tr>
                <td>{{ trade.question[:50] }}</td>
                <td>${{ "%.3f"|format(trade.entry_price) }}</td>
                <td>${{ "%.3f"|format(trade.exit_price) }}</td>
                <td>{{ trade.quantity }}</td>
                <td class="{{ 'positive' if trade.p_l > 0 else 'negative' }}">
                    ${{ "%.2f"|format(trade.p_l) }} ({{ "%.1f%%"|format(trade.p_l_percent) }})
                </td>
                <td>{{ 'WIN' if trade.p_l > 0 else 'LOSS' }}</td>
                <td>{{ trade.exit_time[-8:] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route("/")
def dashboard():
    positions = load_positions()
    trades = load_trades()
    circuit_active = trades.get("circuit_breaker_active", False)
    metrics = trades.get("metrics", {"total_trades": 0, "win_rate": 0, "total_pnl": 0})
    return render_template_string(HTML, positions=positions, trades=trades, metrics=metrics, circuit_active=circuit_active)

@app.route("/api/positions")
def api_positions():
    return jsonify(load_positions())

@app.route("/api/trades")
def api_trades():
    return jsonify(load_trades())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
