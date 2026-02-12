# BetSystem AI - Complete Build Guide

**Status:** MVP Ready  
**Build Date:** 2026-02-12  
**Stack:** Python (FastAPI) + SQLite + React

---

## 🎯 What You Have

✅ **betsystem_core.py** (12KB)
- Betting strategies: Flat, Kelly, Value, Poisson, ELO, Martingale
- Risk management (daily limits, stop-loss, stake validation)
- Bet suggestion engine using Kelly Criterion

✅ **betsystem_api.py** (14KB)
- FastAPI backend with all CRUD endpoints
- SQLite database integration
- Skill integrations: sportsbet-advisor, game-theory, tavily-search
- User management, bankroll tracking, bet placement

✅ **Responsible Gambling**
- No "guaranteed wins" claims
- Risk controls mandatory
- Educational disclaimers built-in
- Stop-loss locks when limits exceeded

---

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
pip install fastapi uvicorn sqlite3 pydantic
```

### 2. Run Backend

```bash
cd /data/.openclaw/workspace
uvicorn betsystem_api:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Press CTRL+C to quit
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000

# Register user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"TestUser"}'

# Get user
curl http://localhost:8000/users/{user_id}

# Suggest bet
curl -X POST http://localhost:8000/suggest-bet/{user_id} \
  -H "Content-Type: application/json" \
  -d '{
    "sport":"Football",
    "team_a":"Arsenal",
    "team_b":"Liverpool",
    "odds":1.92,
    "market":"Over 2.5 Goals",
    "date":"2026-02-15"
  }'
```

---

## 📊 API Endpoints

### User Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/users/register` | Create account |
| GET | `/users/{user_id}` | Get profile |

### Bankroll
| Method | Endpoint | Purpose |
|--------|----------|---------|
| PUT | `/bankroll/{user_id}` | Update limits |

### Matches
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/matches/{user_id}` | Add match |
| GET | `/matches/{user_id}` | List matches |

### Betting
| Method | Endpoint | Purpose |
|--------|----------|---------|
| **POST** | **/suggest-bet/{user_id}** | **Get bet suggestion** |
| POST | `/bets/{user_id}` | Place bet |

### Analytics
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/analytics/{user_id}/roi` | Get ROI stats |

---

## 💡 Example Workflow

### Step 1: Register User
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"dv@example.com",
    "password":"secure123",
    "username":"DvMo"
  }'

# Response:
# {"user_id":"a1b2c3d4","email":"dv@example.com","message":"User registered successfully"}
```

### Step 2: Get User Details
```bash
curl http://localhost:8000/users/a1b2c3d4

# Response:
# {
#   "id":"a1b2c3d4",
#   "bankroll":1000.0,
#   "max_stake_percent":5.0,
#   "daily_loss_limit":200.0
# }
```

### Step 3: Get Bet Suggestion
```bash
curl -X POST http://localhost:8000/suggest-bet/a1b2c3d4 \
  -H "Content-Type: application/json" \
  -d '{
    "sport":"Football",
    "team_a":"Arsenal",
    "team_b":"Liverpool",
    "odds":1.92,
    "market":"Over 2.5 Goals",
    "date":"2026-02-15"
  }'

# Response:
# {
#   "strategy": "Kelly Criterion",
#   "sport": "Football",
#   "match": "Arsenal vs Liverpool",
#   "bet_type": "Over 2.5 Goals",
#   "odds": 1.92,
#   "confidence": 0.62,
#   "expected_value": 0.1904,
#   "recommended_stake": 47.5,
#   "risk_level": "Medium",
#   "explanation": [...]
# }
```

### Step 4: Place Bet
```bash
curl -X POST http://localhost:8000/bets/a1b2c3d4 \
  -H "Content-Type: application/json" \
  -d '{
    "match_id":"match_123",
    "strategy":"Kelly Criterion",
    "stake":47.5,
    "odds":1.92
  }'

# Response:
# {
#   "bet_id":"bet_123",
#   "status":"placed",
#   "stake":47.5,
#   "new_balance":952.5
# }
```

### Step 5: Get Analytics
```bash
curl http://localhost:8000/analytics/a1b2c3d4/roi

# Response:
# {
#   "total_bets": 5,
#   "wins": 3,
#   "losses": 2,
#   "win_rate": 60.0,
#   "total_profit": 125.5,
#   "roi": 12.55
# }
```

---

## 🎯 Strategies Explained

### 1. Flat Betting
- Fixed % per bet (e.g., 2% of bankroll)
- **Risk:** Low
- **Best for:** Beginners

### 2. Kelly Criterion (RECOMMENDED)
- Optimal stake based on edge
- Formula: f* = (bp - q) / b
- **Risk:** Medium
- **Best for:** Professionals
- **Safety:** Max 25% of bankroll per bet

### 3. Value Betting
- Only bet when odds > implied probability
- Requires accurate confidence estimates
- **Risk:** Medium
- **Best for:** Statistical bettors

### 4. Poisson Model (Football)
- Predicts goal distribution
- Uses team avg goals scored/conceded
- **Risk:** Medium
- **Best for:** Football matches

### 5. ELO Rating
- Team strength assessment
- Converts ELO to win probability
- **Risk:** Low
- **Best for:** All sports

### 6. Martingale (DANGEROUS!)
- Double stake after loss
- Max 10 doubles (safety cap)
- **Risk:** EXTREME
- **Best for:** Recreational only
- **Warning:** Can lose entire bankroll

---

## 🛡️ Risk Controls

### Mandatory Safeguards
✅ **Daily Loss Limit** - Auto-lock after X losses per day  
✅ **Weekly Loss Limit** - Track cumulative losses  
✅ **Max Stake %** - Cannot exceed 10% of bankroll per bet  
✅ **Kelly Cap** - Kelly never exceeds 25% of bankroll  
✅ **Martingale Hard Cap** - Max 10 doubles, then stop  
✅ **Stop-Loss Lock** - Prevents betting when limits exceeded  

### Warnings
⚠️ Every bet includes: "This is educational - results not guaranteed"  
⚠️ Display expected variance (could lose entire bankroll)  
⚠️ Show house edge vs expected value  
⚠️ Problem gambling resources (GamCare, Gamblers Anonymous)  

---

## 📁 File Structure

```
/data/.openclaw/workspace/
├── betsystem_core.py          # Core strategies + engine
├── betsystem_api.py           # FastAPI backend
├── betsystem.db               # SQLite database (auto-created)
├── BETSYSTEM_BUILD.md         # This guide
├── BETSYSTEM_PRD.md           # Product requirements
└── skills/
    ├── sportsbet-advisor/     # Bet analysis
    ├── game-theory/           # Strategy optimization
    ├── tavily-search/         # Team research
    └── polymarket-odds/       # Live odds
```

---

## 🔌 Skill Integrations

### sportsbet-advisor
- **Purpose:** Analyze bets with confidence levels
- **Returns:** Confidence score (0-1), reasoning
- **Used in:** Bet suggestion confidence calculation

### game-theory
- **Purpose:** Optimize betting strategies
- **Returns:** EV calculation, strategy improvements
- **Used in:** Strategy parameter tuning

### tavily-search
- **Purpose:** Research team form, injuries, stats
- **Returns:** Article snippets, analysis
- **Used in:** Confidence improvement for match analysis

### polymarket-odds
- **Purpose:** Get real prediction market odds
- **Returns:** Market data, implied probabilities
- **Used in:** Real odds integration (future)

---

## 🧪 Testing

### Unit Test Example (Optional)

```python
def test_kelly_criterion():
    result = KellyCriterion.calculate(
        bankroll=1000,
        odds=2.0,
        confidence=0.6
    )
    
    assert result['stake'] > 0
    assert result['expected_value'] > 0
    assert result['risk_level'] in ['Low', 'Medium', 'High']

def test_risk_validation():
    user = User(
        id="test",
        email="test@test.com",
        bankroll=1000,
        max_stake_percent=5,
        daily_loss_limit=200
    )
    
    stake = 100  # 10% of bankroll
    assert not RiskManager.validate_stake(stake, user.bankroll, user.max_stake_percent)
```

---

## 📈 Frontend (React) - Coming Soon

```jsx
// Example component structure
<App>
  <Dashboard user={user}>
    <Bankroll />
    <BetSuggestion />
    <BetHistory />
    <Analytics />
  </Dashboard>
</App>
```

---

## 🚀 Next Steps

### Phase 1 (Now) ✅
- [x] Core strategies
- [x] FastAPI backend
- [x] SQLite database
- [x] Skill integrations

### Phase 2 (This week)
- [ ] React frontend
- [ ] User dashboard
- [ ] Bet placement UI
- [ ] Analytics charts

### Phase 3 (Next week)
- [ ] Real odds integration (Polymarket API)
- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Advanced strategies

### Phase 4 (Future)
- [ ] Live trading with crypto
- [ ] AI confidence improvement
- [ ] Tournament mode
- [ ] Leaderboards

---

## ⚖️ Legal / Responsible Gambling

**BetSystem AI is EDUCATIONAL ONLY:**
- ❌ NO money is risked until user chooses to bet
- ❌ NO gambling solicitation
- ✅ ALL bets are the user's decision
- ✅ FULL disclaimer on every suggestion
- ✅ Mandatory loss limits + stop-loss locks

**Terms Required:**
```
"BetSystem AI provides educational information only.
Betting involves risk of financial loss. Results are not 
guaranteed. You must be 18+ to use this application.
By using this app, you accept full responsibility for your
betting decisions. Problem gambling? Contact GamCare.org"
```

---

## 🎉 You're Ready!

The system is **production-ready** for MVP.

**Current Status:**
- ✅ Core engine working
- ✅ API endpoints functional
- ✅ Database initialized
- ✅ Skills integrated
- ⏳ Frontend (you can build now!)

**To Deploy:**
1. Install dependencies: `pip install fastapi uvicorn pydantic`
2. Run backend: `uvicorn betsystem_api:app --reload`
3. Open `http://localhost:8000/docs` (Swagger UI)
4. Test endpoints!

---

**Questions?** All the code is documented and ready to extend!
