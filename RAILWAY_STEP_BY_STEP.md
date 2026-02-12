# 🚀 Railway Deployment - Step by Step (With Screenshots)

**Status:** Ready to Deploy  
**Time:** 15 minutes  
**Cost:** $0 (first month free credits)

---

## 📋 Pre-Deployment Checklist

Before you start, make sure you have:

- [ ] GitHub account (login: https://github.com/login)
- [ ] Valid credit card (Railway requires it, won't charge first month)
- [ ] 15 minutes of time
- [ ] This repository ready (all files committed to GitHub)

---

## 🎯 STEP 1: Create Railway Account (2 minutes)

### 1.1 Go to Railway

**URL:** https://railway.app

**Click:** "Start Project" button

### 1.2 Sign Up with GitHub

**Click:** "Continue with GitHub"

**Result:** You'll be redirected to GitHub authorization

### 1.3 Authorize Railway

**Click:** "Authorize Railway" button

**Select:** Your repositories (or allow all)

**Result:** Back at Railway dashboard

---

## 📦 STEP 2: Deploy Backend (5 minutes)

### 2.1 Create New Project

**In Railway Dashboard:**

1. Click **"New Project"** button (top right)
2. Select **"Deploy from GitHub"**
3. Click **"Authorize Railway"** (if not already done)

### 2.2 Select Your Repository

**Search or select:**
- Repository name: `openclaw-workspace` (or your repo name)
- Click on the repository

### 2.3 Configure Deployment

**Railway will:**
- Auto-detect Dockerfile ✅
- Auto-detect railway.toml ✅
- Start building automatically ✅

**Wait:** ~2-3 minutes for build to complete

**You'll see:**
```
✓ Build successful
✓ Deployment in progress
✓ Service running
```

### 2.4 Get Backend URL

**After deployment completes:**

1. Click on the service (should say "Running" in green)
2. Go to "Domains" tab
3. You'll see a public URL like:
   ```
   https://betsystem-api-prod-xyz.railway.app
   ```
4. **COPY AND SAVE THIS URL** ← You'll need it for frontend!

**Test it works:**
```bash
curl https://your-backend-url.railway.app/

# Should return:
# {"status": "✅ BetSystem AI Running"}
```

---

## 🗄️ STEP 3: Create PostgreSQL Database (3 minutes)

### 3.1 Add PostgreSQL Service

**In Railway Dashboard:**

1. Click **"New"** button (top left)
2. Select **"PostgreSQL"**
3. Click **"Create"**

**Wait:** ~1 minute for database to initialize

### 3.2 Connect Database to Backend

**In PostgreSQL Service:**

1. Go to **"Connect"** tab
2. **Copy** the connection string (looks like):
   ```
   postgresql://postgres:password@host:5432/railway
   ```

### 3.3 Add to Backend Environment

**In Backend Service:**

1. Go to **"Variables"** tab
2. Click **"New Variable"**
3. **Key:** `DATABASE_URL`
4. **Value:** (paste the connection string from above)
5. Click **"Add"**
6. Click **"Deploy"** button

**Wait:** ~1 minute for backend to restart with database

**Verify:**
```bash
curl https://your-backend-url.railway.app/health

# Should return 200 OK
```

---

## 🎨 STEP 4: Deploy Frontend (5 minutes)

### 4.1 Create Frontend Service

**In Railway Dashboard:**

1. Click **"New"** button
2. Select **"GitHub Repo"**
3. Search for `betsystem-ui` folder
4. **Important:** Select the `betsystem-ui` subdirectory

### 4.2 Set Environment Variables

**In Frontend Service:**

1. Go to **"Variables"** tab
2. Add two variables:
   ```
   VITE_API_URL = https://your-backend-url.railway.app
   PORT = 3000
   ```

### 4.3 Set Build Command

**In Frontend Service:**

1. Go to **"Settings"** tab
2. Find **"Build Command"**
3. Set to: `npm run build`
4. Find **"Start Command"**
5. Set to: `serve -s dist -l 3000`

### 4.4 Deploy

**Click:** **"Deploy"** button

**Wait:** ~3-5 minutes for build and deployment

**You'll see:**
```
✓ Dependencies installed
✓ Build successful
✓ Deployment in progress
✓ Service running
```

### 4.5 Get Frontend URL

**After deployment:**

1. Click on Frontend service
2. Go to **"Domains"** tab
3. Copy the public URL:
   ```
   https://betsystem-frontend-xyz.railway.app
   ```

---

## ✅ STEP 5: Verify Everything Works (2 minutes)

### 5.1 Test Backend

```bash
# Get your backend URL from Railway
curl https://your-backend.railway.app/

# Expected response:
# {"status": "✅ BetSystem AI Running"}
```

### 5.2 Test Frontend

**Open in browser:**
```
https://your-frontend.railway.app
```

**Expected:**
- Login page loads
- No errors in console (F12)
- Page is responsive

### 5.3 Test API Documentation

**Open in browser:**
```
https://your-backend.railway.app/docs
```

**Expected:**
- Swagger UI loads
- All endpoints listed
- Can test endpoints directly

### 5.4 Test User Registration

**In Swagger UI or terminal:**

```bash
curl -X POST https://your-backend.railway.app/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "username": "testuser"
  }'

# Expected response (201):
# {
#   "id": "user_1",
#   "email": "test@example.com",
#   "username": "testuser"
# }
```

### 5.5 Test Frontend Login

1. Go to https://your-frontend.railway.app
2. Enter:
   - Username: `testuser`
   - Password: `testpass123`
3. Click **"Sign In"**

**Expected:**
- Login succeeds
- Dashboard loads
- Shows "Welcome" message

### 5.6 Test Bet Suggestion

1. On Dashboard, click **"Get Suggestion"** tab
2. Fill in:
   - Team A: `Arsenal`
   - Team B: `Liverpool`
   - Odds: `1.92`
   - Market: `Over 2.5 Goals`
3. Click **"Get Suggestion"**

**Expected:**
- Suggestion card appears
- Shows strategy, confidence, EV
- Recommended stake displays

---

## 🎉 Success! You're Live!

**Your URLs:**
```
Frontend:  https://your-frontend.railway.app
Backend:   https://your-backend.railway.app
API Docs:  https://your-backend.railway.app/docs
```

**Share these with users!**

---

## 📊 Post-Deployment

### Monitor Performance

**In Railway Dashboard:**

1. Click each service
2. Go to **"Metrics"** tab
3. Watch:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### View Logs

**For debugging:**

1. Click service
2. Go to **"Logs"** tab
3. Watch for errors
4. Check response patterns

### Monitor Costs

**In Railway Dashboard:**

1. Click **"Billing"** tab
2. See usage and estimated cost
3. Set spending limit if desired

---

## 🆘 Troubleshooting

### Frontend Shows Blank Page

**Fix:**
1. Check browser console (F12)
2. Look for CORS or API errors
3. Verify VITE_API_URL is correct
4. Redeploy frontend

### Backend Won't Start

**Fix:**
1. Check Backend → Logs
2. Look for error messages
3. Verify DATABASE_URL is set
4. Verify environment variables
5. Click "Deploy" to restart

### Database Connection Error

**Fix:**
1. Verify PostgreSQL is running (green checkmark)
2. Copy fresh connection string from PostgreSQL → Connect
3. Update DATABASE_URL in Backend variables
4. Redeploy backend

### Login Fails

**Fix:**
1. Check backend logs for errors
2. Verify DATABASE_URL is correct
3. Try registering new user first
4. Check if database tables exist

---

## 📋 Deployment Checklist

- [ ] Railway account created
- [ ] Backend deployed and running (green)
- [ ] Backend has public URL (copied)
- [ ] PostgreSQL created and running (green)
- [ ] DATABASE_URL set in Backend variables
- [ ] Frontend deployed and running (green)
- [ ] VITE_API_URL set to backend URL in Frontend variables
- [ ] Backend responds to health check
- [ ] Frontend loads in browser
- [ ] Swagger UI accessible at /docs
- [ ] Can register new user
- [ ] Can login with test credentials
- [ ] Dashboard loads after login
- [ ] Bet suggestion form works
- [ ] All tests passing ✅

---

## 💰 Cost Summary

**First Month:** $0 (using $5 Railway credits)

**After that:**
```
Backend compute:    $5-20/month
PostgreSQL:         $7-15/month
Total:              $12-35/month
```

**View at:** Railway Dashboard → Billing tab

---

## 🎯 You're Done!

**Congratulations! 🎉**

Your BetSystem AI is now **live in production**!

**What's next?**
1. Share frontend URL with users
2. Monitor performance in Railway dashboard
3. Watch for errors in logs
4. Update custom domain (optional)
5. Add monitoring/analytics

---

## 📞 Need Help?

**Documentation:**
- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev

**Common Issues:**
- See `RAILWAY_DEPLOYMENT.md` for detailed troubleshooting
- Check `TEST_SUITE.md` for verification tests

---

**Ready?** Follow the steps above and you'll be live in 15 minutes! 🚀
