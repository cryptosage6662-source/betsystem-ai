# BetSystem AI - Complete Test Suite

**Run these tests to verify system is working:**

---

## 🧪 Test 1: Backend Health Check

**Purpose:** Verify backend is running and responding

```bash
# Start backend first:
python3 -m uvicorn betsystem_api:app --host 0.0.0.0 --port 8000

# In another terminal, test:
curl -X GET http://localhost:8000/

# Expected response (200 OK):
# {"status": "✅ BetSystem AI Running"}
```

✅ **Pass if:** Response is 200 and shows status message

---

## 🧪 Test 2: API Documentation

**Purpose:** Verify Swagger UI is accessible

```bash
# Open in browser:
# http://localhost:8000/docs

# Or test via curl:
curl -s http://localhost:8000/docs | grep -i swagger
```

✅ **Pass if:** Swagger UI loads with all endpoints listed

---

## 🧪 Test 3: User Registration

**Purpose:** Create new user account

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "username": "testuser"
  }'
```

✅ **Pass if:** Response is 201 and includes `user_id`

---

## 🧪 Test 4: User Login

**Purpose:** Authenticate user

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

✅ **Pass if:** Response includes `access_token` and `token_type`

---

## 🧪 Test 5: Get Bankroll

**Purpose:** Fetch user bankroll info

```bash
curl -X GET http://localhost:8000/bankroll/user_1 \
  -H "Content-Type: application/json"
```

✅ **Pass if:** Response includes `current`, `starting`, `roi`

---

## 🧪 Test 6: Suggest Bet

**Purpose:** Generate bet suggestion

```bash
curl -X POST http://localhost:8000/suggest-bet/user_1 \
  -H "Content-Type: application/json" \
  -d '{
    "sport": "Football",
    "team_a": "Arsenal",
    "team_b": "Liverpool",
    "odds": 1.92,
    "market": "Over 2.5 Goals",
    "date": "2026-02-15"
  }'
```

✅ **Pass if:** Response includes:
  - `strategy`
  - `recommended_stake`
  - `confidence`
  - `expected_value`

---

## 🧪 Test 7: Place Bet

**Purpose:** Create a bet record

```bash
curl -X POST http://localhost:8000/bets/user_1 \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "match_123",
    "odds": 1.92,
    "stake": 50.0,
    "bet_type": "Over 2.5 Goals",
    "status": "active"
  }'
```

✅ **Pass if:** Response includes `bet_id` and status `active`

---

## 🧪 Test 8: Get Bet History

**Purpose:** Retrieve user's bet history

```bash
curl -X GET http://localhost:8000/bets/user_1 \
  -H "Content-Type: application/json"
```

✅ **Pass if:** Response is array of bets with:
  - `bet_id`
  - `odds`
  - `stake`
  - `status`

---

## 🧪 Test 9: Get Analytics

**Purpose:** Fetch ROI and performance stats

```bash
curl -X GET http://localhost:8000/analytics/user_1/roi \
  -H "Content-Type: application/json"
```

✅ **Pass if:** Response includes:
  - `roi_percent`
  - `total_bets`
  - `win_rate`
  - `avg_win`
  - `avg_loss`

---

## 🧪 Test 10: Database Connection

**Purpose:** Verify database is connected

```bash
# Check if betsystem.db exists:
ls -lah betsystem.db

# Test queries:
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('betsystem.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"✅ Database connected. Tables: {len(tables)}")
for table in tables:
    print(f"   - {table[0]}")
EOF
```

✅ **Pass if:** Database exists and contains tables

---

## 🧪 Integration Test Suite

**Run all tests automatically:**

```bash
#!/bin/bash

echo "Running Full Test Suite..."
BASE_URL="http://localhost:8000"

# Test 1: Health
echo -n "1. Health check... "
curl -s $BASE_URL/ | grep -q "status" && echo "✅" || echo "❌"

# Test 2: Register
echo -n "2. User registration... "
curl -s -X POST $BASE_URL/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test","username":"test"}' \
  | grep -q "user_id" && echo "✅" || echo "❌"

# Test 3: Login
echo -n "3. User login... "
curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' \
  | grep -q "access_token" && echo "✅" || echo "❌"

# Test 4: Bankroll
echo -n "4. Get bankroll... "
curl -s $BASE_URL/bankroll/user_1 | grep -q "current" && echo "✅" || echo "❌"

# Test 5: Suggest
echo -n "5. Bet suggestion... "
curl -s -X POST $BASE_URL/suggest-bet/user_1 \
  -H "Content-Type: application/json" \
  -d '{"sport":"Football","team_a":"A","team_b":"B","odds":1.92,"market":"Over","date":"2026-02-15"}' \
  | grep -q "strategy" && echo "✅" || echo "❌"

echo ""
echo "Test suite complete!"
```

---

## 🧪 Frontend Tests

### Test 1: React App Loads

```bash
# Start frontend
cd betsystem-ui
npm install
npm run dev

# Open browser: http://localhost:5173
# Expected: BetSystem AI logo visible
```

✅ **Pass if:** App loads without errors

### Test 2: Login Form Works

```
1. Go to http://localhost:5173
2. Click "Login"
3. Enter username: test, password: test
4. Click "Sign In"
5. Expected: Dashboard loads
```

✅ **Pass if:** Dashboard shows after login

### Test 3: Bet Suggestion Works

```
1. Dashboard loaded
2. Click "Get Suggestion" tab
3. Fill form:
   - Team A: Arsenal
   - Team B: Liverpool
   - Odds: 1.92
   - Market: Over 2.5 Goals
4. Click "Get Suggestion"
5. Expected: Suggestion card appears
```

✅ **Pass if:** Suggestion displays with confidence, EV, stake

### Test 4: Mobile Responsive

```
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on mobile viewport (375x667)
4. Expected: Layout adapts, readable on mobile
```

✅ **Pass if:** All elements visible and clickable on mobile

---

## 📊 Performance Tests

### Test 1: Backend Response Time

```bash
# Should be <500ms
time curl http://localhost:8000/
```

✅ **Pass if:** Response time <500ms

### Test 2: API Endpoint Speed

```bash
# Test multiple endpoints
for i in {1..10}; do
  curl -s http://localhost:8000/bankroll/user_1 > /dev/null
done
echo "✅ 10 requests completed"
```

✅ **Pass if:** All requests complete quickly

### Test 3: Frontend Load Time

```bash
# Use browser DevTools
# Open http://localhost:5173
# Check Network tab
# Expected: Page load <3 seconds
```

✅ **Pass if:** Total load time <3s

---

## 🔐 Security Tests

### Test 1: Invalid Credentials

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"invalid","password":"wrong"}'
```

✅ **Pass if:** Returns 401 Unauthorized

### Test 2: Missing Required Fields

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com"}'
```

✅ **Pass if:** Returns 422 Validation Error

### Test 3: SQL Injection Protection

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass","username":"admin\";DROP TABLE users;--"}'
```

✅ **Pass if:** Username is safely escaped, no SQL error

---

## ✅ Full Test Checklist

- [ ] Backend starts without errors
- [ ] API documentation accessible
- [ ] User registration works
- [ ] User login works
- [ ] Bankroll retrieval works
- [ ] Bet suggestions work
- [ ] Bet placement works
- [ ] Bet history retrieves correctly
- [ ] Analytics endpoint works
- [ ] Database connected
- [ ] Frontend loads without errors
- [ ] Login form works
- [ ] Dashboard displays
- [ ] Bet suggestion form works
- [ ] Mobile responsive
- [ ] Response times <500ms
- [ ] Invalid credentials rejected
- [ ] Required fields validated
- [ ] SQL injection protected

---

## 🚀 Ready for Deployment?

If all tests pass ✅, your BetSystem AI is ready for production!

**Next:** Deploy to Railway.app following `RAILWAY_DEPLOYMENT.md`

---

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

Backend Tests:
- Health Check: ☐ Pass  ☐ Fail
- API Docs: ☐ Pass  ☐ Fail
- Registration: ☐ Pass  ☐ Fail
- Login: ☐ Pass  ☐ Fail
- Bankroll: ☐ Pass  ☐ Fail

Frontend Tests:
- App Loads: ☐ Pass  ☐ Fail
- Login Works: ☐ Pass  ☐ Fail
- Dashboard: ☐ Pass  ☐ Fail
- Suggestions: ☐ Pass  ☐ Fail
- Mobile: ☐ Pass  ☐ Fail

Performance:
- Response Time: ☐ <500ms  ☐ >500ms
- Load Time: ☐ <3s  ☐ >3s

Security:
- Invalid Login: ☐ Blocked  ☐ Accepted
- SQL Injection: ☐ Protected  ☐ Vulnerable

Overall Status: ☐ PASS  ☐ FAIL

Notes: _______________________________
```
