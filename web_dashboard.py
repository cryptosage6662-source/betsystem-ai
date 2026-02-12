#!/usr/bin/env python3
"""
Polymarket Trading Web Dashboard
Flask app for real-time portfolio monitoring
Access via: http://your-server:5000
"""

from flask import Flask, render_template_string, jsonify
import json
import os
import statistics
from datetime import datetime

app = Flask(__name__)

# File paths
POSITION_FILE = "/root/polymarket_trading/positions.json"
TRADES_FILE = "/root/polymarket_trading/trades.json"
EQUITY_FILE = "/root/polymarket_trading/equity_live.json"

def load_positions():
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"positions": [], "cash": 100.0, "equity": 100.0, "max_drawdown": 0.0, "consecutive_losses": 0}

def load_trades():
    if os.path.exists(TRADES_FILE):
        try:
            with open(TRADES_FILE) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            pass
    return []

def load_equity_history():
    if os.path.exists(EQUITY_FILE):
        try:
            with open(EQUITY_FILE) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            pass
    return []

def calculate_metrics(trades, equity_history):
    sells = [t for t in trades if t["type"] == "SELL"]
    if not sells:
        return {
            "total_trades": 0, "winning_trades": 0, "losing_trades": 0,
            "win_rate": 0.0, "total_pnl": 0.0, "avg_win": 0.0, "avg_loss": 0.0,
            "profit_factor": 0.0, "max_drawdown": 0.0, "sharpe_ratio": 0.0
        }
    
    wins = [t["realized_pnl"] for t in sells if t["realized_pnl"] > 0]
    losses = [t["realized_pnl"] for t in sells if t["realized_pnl"] <= 0]
    
    total_pnl = sum(t["realized_pnl"] for t in sells)
    win_rate = len(wins) / len(sells) if sells else 0
    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = statistics.mean(losses) if losses else 0
    gross_profit = sum(wins) if wins else 0
    gross_loss = abs(sum(losses)) if losses else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    if equity_history:
        equities = [e["equity"] for e in equity_history]
        max_drawdown = max([(equities[0] - e) / equities[0] for e in equities] + [0])
        if len(equities) > 1:
            returns = [(equities[i+1] - equities[i]) / equities[i] for i in range(len(equities)-1)]
            sharpe_ratio = (statistics.mean(returns) * 252) / (statistics.stdev(returns) * (252**0.5)) if returns and statistics.stdev(returns) > 0 else 0.0
        else:
            sharpe_ratio = 0.0
    else:
        max_drawdown, sharpe_ratio = 0.0, 0.0
    
    return {
        "total_trades": len(sells), "winning_trades": len(wins), "losing_trades": len(losses),
        "win_rate": win_rate, "total_pnl": total_pnl, "avg_win": avg_win, "avg_loss": avg_loss,
        "profit_factor": profit_factor, "max_drawdown": max_drawdown, "sharpe_ratio": sharpe_ratio
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Polymarket Trading Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { color: #94a3b8; font-size: 14px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .card h2 { font-size: 14px; color: #94a3b8; text-transform: uppercase; margin-bottom: 15px; }
        .card .value { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
        .card .label { font-size: 12px; color: #64748b; }
        .positive { color: #22c55e; }
        .negative { color: #ef4444; }
        .neutral { color: #3b82f6; }
        .table-container { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; margin-bottom: 20px; overflow-x: auto; }
        .table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .table th { text-align: left; padding: 12px; color: #94a3b8; border-bottom: 1px solid #334155; font-weight: 600; }
        .table td { padding: 12px; border-bottom: 1px solid #334155; }
        .table tr:hover { background: #0f172a; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .badge.mean-reversion { background: #3b82f6; color: white; }
        .badge.reversal { background: #f59e0b; color: white; }
        .badge.buy { background: #22c55e; color: white; }
        .badge.sell { background: #ef4444; color: white; }
        .refresh-btn { background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; margin-bottom: 20px; }
        .refresh-btn:hover { background: #2563eb; }
        .time { color: #64748b; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Polymarket Trading Dashboard</h1>
            <p>Real-time portfolio monitoring • Auto-refresh every 5s</p>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Now</button>
        
        <!-- Portfolio Stats -->
        <div class="grid">
            <div class="card">
                <h2>💰 Bankroll</h2>
                <div class="value">${{ portfolio.cash|round(2) }}</div>
                <div class="label">Available Cash</div>
            </div>
            <div class="card">
                <h2>📈 Total Equity</h2>
                <div class="value">${{ portfolio.equity|round(2) }}</div>
                <div class="label">Current Portfolio Value</div>
            </div>
            <div class="card">
                <h2>💹 P&L</h2>
                <div class="value {% if pnl_value >= 0 %}positive{% else %}negative{% endif %}">
                    ${{ (portfolio.equity - 100)|round(2) }}<br>
                    <span class="label" style="color: inherit;">{{ pnl_pct|round(2) }}%</span>
                </div>
            </div>
            <div class="card">
                <h2>📉 Max Drawdown</h2>
                <div class="value negative">{{ (portfolio.max_drawdown * 100)|round(2) }}%</div>
                <div class="label">Largest Loss from Peak</div>
            </div>
        </div>
        
        <!-- Performance Metrics -->
        <div class="table-container">
            <h2 style="margin-bottom: 15px;">📊 Performance Metrics</h2>
            <table class="table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Trades</td>
                    <td><strong>{{ metrics.total_trades }}</strong></td>
                </tr>
                <tr>
                    <td>Winning Trades</td>
                    <td><span class="positive">{{ metrics.winning_trades }}</span></td>
                </tr>
                <tr>
                    <td>Losing Trades</td>
                    <td><span class="negative">{{ metrics.losing_trades }}</span></td>
                </tr>
                <tr>
                    <td>Win Rate</td>
                    <td><strong>{{ (metrics.win_rate * 100)|round(1) }}%</strong></td>
                </tr>
                <tr>
                    <td>Average Win</td>
                    <td><span class="positive">${{ metrics.avg_win|round(2) }}</span></td>
                </tr>
                <tr>
                    <td>Average Loss</td>
                    <td><span class="negative">${{ metrics.avg_loss|round(2) }}</span></td>
                </tr>
                <tr>
                    <td>Profit Factor</td>
                    <td><strong>{{ metrics.profit_factor|round(2) }}x</strong></td>
                </tr>
                <tr>
                    <td>Sharpe Ratio</td>
                    <td><strong>{{ metrics.sharpe_ratio|round(2) }}</strong></td>
                </tr>
            </table>
        </div>
        
        <!-- Open Positions -->
        {% if positions.positions %}
        <div class="table-container">
            <h2 style="margin-bottom: 15px;">🔓 Open Positions ({{ positions.positions|length }})</h2>
            <table class="table">
                <tr>
                    <th>Market</th>
                    <th>Entry Price</th>
                    <th>Current Price</th>
                    <th>P&L</th>
                    <th>Strategy</th>
                </tr>
                {% for pos in positions.positions %}
                <tr>
                    <td>{{ pos.market_question[:40] }}</td>
                    <td>${{ pos.entry_price|round(3) }}</td>
                    <td>${{ pos.current_price|round(3) }}</td>
                    <td>
                        <span class="{% if pos.unrealized_pnl >= 0 %}positive{% else %}negative{% endif %}">
                            ${{ pos.unrealized_pnl|round(2) }} ({{ (pos.unrealized_pnl_pct * 100)|round(2) }}%)
                        </span>
                    </td>
                    <td><span class="badge {% if pos.strategy == 'mean_reversion' %}mean-reversion{% else %}reversal{% endif %}">{{ pos.strategy }}</span></td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}
        
        <!-- Recent Trades -->
        {% if trades %}
        <div class="table-container">
            <h2 style="margin-bottom: 15px;">💬 Recent Trades (Last 10)</h2>
            <table class="table">
                <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Market</th>
                    <th>Price</th>
                    <th>P&L</th>
                    <th>Strategy</th>
                </tr>
                {% for trade in trades[-10:]|reverse %}
                <tr>
                    <td class="time">{{ trade.timestamp.split('T')[1][:5] }}</td>
                    <td><span class="badge {% if trade.type == 'BUY' %}buy{% else %}sell{% endif %}">{{ trade.type }}</span></td>
                    <td>{{ trade.market[:35] }}</td>
                    <td>${{ trade.price|round(3) }}</td>
                    <td>
                        {% if trade.type == 'SELL' %}
                        <span class="{% if trade.realized_pnl >= 0 %}positive{% else %}negative{% endif %}">
                            ${{ trade.realized_pnl|round(2) }}
                        </span>
                        {% else %}
                        -
                        {% endif %}
                    </td>
                    <td>{{ trade.get('strategy', 'N/A') }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #64748b; font-size: 12px;">
            <p>Last updated: {{ now }}</p>
            <p>Page auto-refreshes every 5 seconds</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    positions = load_positions()
    trades = load_trades()
    equity_history = load_equity_history()
    metrics = calculate_metrics(trades, equity_history)
    
    pnl_value = positions.get('equity', 100) - 100
    pnl_pct = (pnl_value / 100) * 100 if pnl_value != 0 else 0
    
    return render_template_string(
        HTML_TEMPLATE,
        portfolio=positions,
        trades=trades,
        equity_history=equity_history,
        metrics=metrics,
        pnl_value=pnl_value,
        pnl_pct=pnl_pct,
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/data')
def api_data():
    positions = load_positions()
    trades = load_trades()
    equity_history = load_equity_history()
    metrics = calculate_metrics(trades, equity_history)
    
    return jsonify({
        'portfolio': positions,
        'trades': trades,
        'equity_history': equity_history,
        'metrics': metrics
    })

if __name__ == '__main__':
    print("🌐 Starting Polymarket Web Dashboard...")
    print("📱 Access at: http://localhost:5000")
    print("🔄 Auto-refresh every 5 seconds")
    app.run(host='0.0.0.0', port=5000, debug=False)
