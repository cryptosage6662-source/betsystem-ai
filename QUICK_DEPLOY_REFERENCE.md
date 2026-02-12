# 🚀 BetSystem AI - Quick Deploy Reference

**Keep this tab open while deploying!**

---

## 🎯 Deploy in 4 Steps (15 min)

### 1️⃣ Sign Up Railway (2 min)
```
https://railway.app
→ "Start Project"
→ "Deploy from GitHub"
→ Authorize & select repo
→ Click "Deploy"
```

### 2️⃣ Create Database (3 min)
```
Railway Dashboard
→ "New" → "PostgreSQL"
→ Wait for creation
→ Copy connection string
→ Backend → Variables → DATABASE_URL = (paste)
→ Deploy
```

### 3️⃣ Deploy Frontend (5 min)
```
Railway Dashboard
→ "New" → "GitHub Repo"
→ Select betsystem-ui
→ Build: npm run build
→ Add VITE_API_URL = (your backend URL)
→ Deploy
```

### 4️⃣ Test (2 min)
```
✅ curl https://your-backend/
✅ Open https://your-frontend/ in browser
✅ Test login with testuser/test123
✅ Try bet suggestion
```

---

## 📍 URLs You Need

```
Backend URL:  https://_______________________.railway.app
Frontend URL: https://_______________________.railway.app
DB String:    postgresql://________________:5432/___________
```

---

## 🧪 Quick Tests

```bash
# Test backend
curl https://your-backend.railway.app/

# Test API docs
curl https://your-backend.railway.app/docs

# Test register
curl -X POST https://your-backend.railway.app/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","username":"test"}'

# Test login
curl -X POST https://your-backend.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

---

## ⚠️ Common Issues

| Problem | Fix |
|---------|-----|
| Frontend blank page | Check browser F12 console, verify VITE_API_URL |
| Backend won't start | Check logs, verify DATABASE_URL is set |
| Database error | Copy fresh connection string, re-paste in variables |
| Login fails | Verify backend is running, database connected |

---

## 💰 Cost

```
First month:  $0 (Railway $5 credits)
After:        $12-35/month
Check:        Railway Dashboard → Billing
```

---

## 📚 Detailed Guides

- **Full Steps:** RAILWAY_STEP_BY_STEP.md
- **Troubleshooting:** RAILWAY_DEPLOYMENT.md
- **Testing:** TEST_SUITE.md
- **Costs:** DEPLOYMENT_COSTS.md

---

## ✅ When You're Done

```
Frontend:    https://your-frontend.railway.app ← Share this!
Backend API: https://your-backend.railway.app
API Docs:    https://your-backend.railway.app/docs
Status:      🟢 LIVE IN PRODUCTION
```

---

**START HERE:** https://railway.app 🚀
