# BetSystem AI - Product Requirements Document

**Version:** 1.0  
**Status:** MVP  
**Build Start:** 2026-02-12

---

## 1. Executive Summary

**BetSystem AI** is an educational sports betting strategy application that helps users:
- Safely manage bankroll with built-in risk controls
- Apply data-driven betting strategies (educational only)
- Track performance with ROI, yield, and drawdown metrics
- Receive bet suggestions with confidence levels and EV calculations

**Core Philosophy:** Teach responsible betting through math, not luck.

---

## 2. MVP Scope (Phase 1)

### 2.1 User Management
- ✅ Registration + Login (email/password)
- ✅ User profile (name, timezone, preferences)
- ✅ Password reset
- ✅ Terms acceptance (responsible gambling)

### 2.2 Bankroll Management
- ✅ Set starting bankroll ($50-$50,000)
- ✅ Configure per-bet stake % (1%-10%)
- ✅ Daily/weekly loss limits
- ✅ Auto stop-loss lock (freezes betting)
- ✅ Real-time bankroll tracking

### 2.3 Matches & Odds
- ✅ Manual odds input (no API yet)
- ✅ Sport selection (Football, Basketball, Tennis)
- ✅ Match info: teams, date, odds
- ✅ Multiple markets (Moneyline, Over/Under, Spreads)

### 2.4 Strategy Engine (Modular)
- ✅ Flat Betting (fixed % per bet)
- ✅ Kelly Criterion (optimized stake %)
- ✅ Value Betting (odds vs probability)
- ✅ Poisson Model (football goal predictions)
- ✅ ELO Rating Model (team strength)
- ✅ Martingale (with hard safety limits)

### 2.5 Bet Suggestions
**Output Format (JSON):**
```json
{
  "strategy": "Value Betting",
  "sport": "Football",
  "match": "Arsenal vs Liverpool",
  "bet_type": "Over 2.5 Goals",
  "odds": 1.92,
  "confidence": 0.64,
  "expected_value": 0.10,
  "recommended_stake": 2.0,
  "stake_unit": "percent_bankroll",
  "risk_level": "Medium",
  "explanation": [
    "Arsenal scores avg 2.1 goals/game",
    "Liverpool concedes avg 1.8 goals/game",
    "Poisson model: 72% chance of 3+ goals",
    "Odds imply 52% probability",
    "EV = (0.72 * 1.92) - 1 = +0.38"
  ]
}
```

### 2.6 Tracking Dashboard
- ✅ Bet history (all bets placed)
- ✅ Win/Loss stats
- ✅ ROI % (return on investment)
- ✅ Yield % (profit / total staked)
- ✅ Max Drawdown
- ✅ Profit/Loss charts
- ✅ Strategy performance breakdown

### 2.7 Risk Controls (MANDATORY)
- ✅ Daily loss limit (% of bankroll)
- ✅ Weekly loss limit
- ✅ Max stake % per bet
- ✅ Martingale hard cap (max 10 doubles)
- ✅ Auto stop-loss lock (prevents betting)
- ✅ Responsible gambling warnings

---

## 3. Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite (MVP), PostgreSQL (production)
- **Auth:** JWT tokens
- **Task Queue:** (Optional) Celery for strategy calculations

### Frontend
- **Framework:** React.js (web)
- **UI:** Tailwind CSS + shadcn/ui
- **Charts:** Chart.js or Recharts
- **State:** Redux

### Deployment
- **Backend:** Docker + Heroku/Railway
- **Frontend:** Vercel
- **Database:** Supabase (PostgreSQL)

---

## 4. Database Schema (SQLite/PostgreSQL)

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  username VARCHAR,
  timezone VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  terms_accepted BOOLEAN,
  risk_profile VARCHAR (low|medium|high)
);
```

### Bankroll Table
```sql
CREATE TABLE bankrolls (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  starting_amount DECIMAL(10,2),
  current_amount DECIMAL(10,2),
  max_stake_percent DECIMAL(5,2),
  daily_loss_limit DECIMAL(10,2),
  weekly_loss_limit DECIMAL(10,2),
  stop_loss_locked BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Matches Table
```sql
CREATE TABLE matches (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  sport VARCHAR (Football|Basketball|Tennis),
  team_a VARCHAR,
  team_b VARCHAR,
  match_date TIMESTAMP,
  market_type VARCHAR,
  odds DECIMAL(5,2),
  created_at TIMESTAMP
);
```

### Bets Table
```sql
CREATE TABLE bets (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  match_id UUID FOREIGN KEY,
  strategy VARCHAR,
  stake DECIMAL(10,2),
  odds DECIMAL(5,2),
  confidence DECIMAL(3,2),
  expected_value DECIMAL(5,2),
  result VARCHAR (pending|win|loss),
  profit_loss DECIMAL(10,2),
  placed_at TIMESTAMP,
  resolved_at TIMESTAMP
);
```

### Strategies Table
```sql
CREATE TABLE strategy_configs (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  strategy_name VARCHAR,
  enabled BOOLEAN,
  parameters JSON,
  created_at TIMESTAMP
);
```

---

## 5. API Endpoints (FastAPI)

### Auth
- `POST /auth/register` - Register user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh JWT
- `POST /auth/logout` - Logout

### Bankroll
- `GET /bankroll` - Get current bankroll
- `PUT /bankroll` - Update settings
- `GET /bankroll/history` - Daily balance history
- `POST /bankroll/lock` - Manual stop-loss lock

### Matches
- `POST /matches` - Create match
- `GET /matches` - List matches
- `PUT /matches/{id}` - Update match

### Strategies
- `GET /strategies` - List available strategies
- `POST /strategies/{name}/suggest` - Get bet suggestion
- `GET /strategy/{name}/config` - Get strategy settings
- `PUT /strategy/{name}/config` - Update settings

### Bets
- `POST /bets` - Place bet
- `GET /bets` - Get bet history
- `PUT /bets/{id}/resolve` - Resolve bet (win/loss)
- `GET /bets/stats` - Get performance stats

### Analytics
- `GET /analytics/roi` - ROI, Yield, Drawdown
- `GET /analytics/by-strategy` - Performance by strategy
- `GET /analytics/charts` - Chart data

---

## 6. Strategy Engine

### Strategy Interface
```python
class BettingStrategy:
    def calculate(self, match, bankroll, odds, confidence) -> BetSuggestion:
        """Calculate recommended stake and EV"""
        pass
```

### Available Strategies
1. **Flat Betting** - Fixed % of bankroll per bet
2. **Kelly Criterion** - Optimal stake based on edge
3. **Value Betting** - Bet when odds > implied probability
4. **Poisson Model** - Goal prediction for football
5. **ELO Rating** - Team strength assessment
6. **Martingale** - Double stake after loss (MAX 10x)

---

## 7. Responsible Gambling

### MANDATORY Warnings
- ❌ NO "Guaranteed Wins" claims
- ⚠️ "This is educational - results not guaranteed"
- 🛑 Daily/weekly loss limits (hard stop)
- 📊 Display expected drawdown
- 💰 Show house edge vs expected value

### User Agreements
- Must accept Terms before betting
- Explain variance and risk
- Provide problem gambling resources (GamCare, Gamblers Anonymous)
- Mandatory cooling-off period (optional feature)

---

## 8. Build Phases

### Phase 1 (Week 1) - MVP Backend
- [ ] Database setup (SQLite)
- [ ] FastAPI skeleton
- [ ] User auth (JWT)
- [ ] Bankroll API
- [ ] Strategy engine (3 strategies)
- [ ] Bet suggestion API

### Phase 2 (Week 2) - Frontend MVP
- [ ] Login/Register UI
- [ ] Bankroll dashboard
- [ ] Match input form
- [ ] Bet suggestion display
- [ ] Bet history table

### Phase 3 (Week 3) - Analytics
- [ ] ROI/Yield calculations
- [ ] Performance charts
- [ ] Strategy breakdown
- [ ] Risk controls UI

### Phase 4 (Week 4) - Polish + Testing
- [ ] Unit tests (backend)
- [ ] E2E tests (frontend)
- [ ] Deployment guide
- [ ] Documentation

---

## 9. Success Metrics

✅ **Must Have:**
- Users can input matches + odds
- System generates bet suggestions (JSON format)
- Bankroll is tracked in real-time
- Loss limits are enforced
- No crashes or errors

✅ **Nice to Have:**
- Beautiful charts
- Mobile responsive
- Multiple strategies working

---

## 10. Timeline

**Start:** 2026-02-12  
**MVP Ready:** 2026-02-26 (2 weeks)

---

**Next:** Build database schema + FastAPI skeleton
