# BetSystem AI - Railway.app Deployment Guide

**Estimated Setup Time:** 15 minutes  
**Monthly Cost:** $12-35  
**Difficulty:** ⭐ Easy

---

## 🚀 Step 1: Create Railway Account (2 minutes)

1. Go to **https://railway.app**
2. Click **"Start Project"**
3. Sign up with GitHub (easiest)
4. Authorize Railway to access your repos

---

## 📦 Step 2: Deploy Backend (5 minutes)

### Option A: Deploy from GitHub (Recommended)

1. In Railway dashboard, click **"New Project"**
2. Select **"GitHub Repo"**
3. Search for your repo (or fork this one)
4. Select the repo
5. Click **"Deploy Now"**

Railway will:
- ✅ Detect Dockerfile
- ✅ Build image
- ✅ Deploy to production
- ✅ Get public URL

### Option B: Deploy from CLI

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
cd /data/.openclaw/workspace
railway up

# 4. Get URL
railway domain
```

---

## 🗄️ Step 3: Setup Database (3 minutes)

### In Railway Dashboard:

1. **Create PostgreSQL database:**
   - Click "New Service"
   - Select "PostgreSQL"
   - Click "Create"

2. **Get Connection String:**
   - PostgreSQL service → "Connect"
   - Copy the connection string
   - Format: `postgresql://user:pass@host:5432/db`

3. **Set Environment Variable:**
   - Backend service → "Variables"
   - Add `DATABASE_URL` = (your connection string)
   - Deploy

---

## 🎨 Step 4: Deploy Frontend (5 minutes)

### In Railway Dashboard:

1. **Create new service for frontend**
2. **Connect your `betsystem-ui` GitHub repo**
3. **Set environment variables:**
   ```
   VITE_API_URL = https://your-backend.railway.app
   ```
4. **Set build command:**
   ```
   npm run build
   ```
5. **Deploy**

---

## ✅ Step 5: Test Deployment (1 minute)

### Test Backend API:

```bash
# Get your backend URL from Railway dashboard
curl https://your-backend.railway.app/

# Expected response:
# {"status": "✅ BetSystem AI Running"}

# Test API docs:
# https://your-backend.railway.app/docs
```

### Test Frontend:

```bash
# Visit your frontend URL
https://your-frontend.railway.app
```

### Test Database Connection:

```bash
curl https://your-backend.railway.app/health
# Should return 200 OK
```

---

## 🔧 Environment Variables

Create `.env` file in repo root:

```env
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/betsystem
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_HOSTS=your-domain.com,*.railway.app

# Frontend
VITE_API_URL=https://your-backend.railway.app
```

---

## 📊 Verification Checklist

After deployment, verify:

- [ ] Backend running: `curl https://your-backend.railway.app/`
- [ ] API docs accessible: `https://your-backend.railway.app/docs`
- [ ] Frontend loads: `https://your-frontend.railway.app`
- [ ] Database connected: Check Railway dashboard
- [ ] No errors in logs: Railway → Backend → Logs

---

## 🎯 Testing the Full System

### 1. Register User

```bash
curl -X POST https://your-backend.railway.app/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "testpass123",
    "username": "testuser"
  }'
```

Expected response:
```json
{
  "id": "user_1",
  "email": "test@test.com",
  "username": "testuser"
}
```

### 2. Login

```bash
curl -X POST https://your-backend.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

### 3. Get Bet Suggestion

```bash
curl -X POST https://your-backend.railway.app/suggest-bet/user_1 \
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

Expected response:
```json
{
  "strategy": "Kelly Criterion",
  "recommended_stake": 50.00,
  "confidence": 0.75,
  "expected_value": 0.15,
  "risk_level": "Medium"
}
```

### 4. Test Frontend

Visit `https://your-frontend.railway.app`:
1. Click "Login" (or signup)
2. Enter test credentials
3. View Dashboard
4. Go to "Get Suggestion"
5. Fill in a bet
6. Click "Get Suggestion"
7. See results display

---

## 🛠️ Troubleshooting

### Problem: Backend won't start

**Check logs:**
```
Railway → Backend → Logs tab
```

**Common issues:**
- Missing PostgreSQL environment variable
- Database connection failed
- Wrong port (should be 8000)

**Fix:**
```
Set DATABASE_URL environment variable in Railway → Backend → Variables
```

### Problem: Frontend shows blank page

**Check browser console:**
- Press F12
- Look for error messages
- Check network tab

**Common issues:**
- VITE_API_URL not set
- API URL wrong/unreachable
- CORS errors

**Fix:**
```
1. Set VITE_API_URL = https://your-backend.railway.app
2. Redeploy frontend
3. Clear browser cache (Ctrl+Shift+Del)
```

### Problem: Database connection failed

**Verify connection string:**
```
Railway → PostgreSQL → "Connect" tab → Copy connection string
Paste into Backend → Variables → DATABASE_URL
```

**Test connection:**
```bash
psql "your-connection-string" -c "SELECT 1"
```

---

## 📈 Monitoring

### View Logs

```
Railway Dashboard → Your Service → Logs tab
```

### Monitor Performance

```
Railway Dashboard → Your Service → Metrics tab
- CPU usage
- Memory usage
- Network I/O
- Request latency
```

### Setup Alerts (Optional)

```
Railway Dashboard → Settings → Notifications
- Enable email alerts
- Alert on deployment failure
- Alert on resource limits
```

---

## 💰 Cost Monitoring

### View Bill

```
Railway Dashboard → Billing tab
```

You'll see:
- Compute hours used
- Database storage
- Data transfer
- Estimated monthly cost

**Default limit:** $5/month (free credits)  
**Max limit:** $100/month (configurable)

---

## 🔐 Security Setup

### Enable Custom Domain

1. Railway → Backend → Settings
2. "Custom Domain"
3. Add your domain (e.g., `api.yourdomain.com`)
4. Update DNS records as shown
5. SSL auto-configured

### Update Environment Variables

```
DATABASE_URL = your-production-db-string
DEBUG = False
SECRET_KEY = generate-a-random-key-here
ALLOWED_HOSTS = yourdomain.com,*.yourdomain.com
```

---

## 🚀 Go Live Checklist

- [ ] Backend deployed and running
- [ ] Frontend deployed and running
- [ ] Database connected
- [ ] All tests passing
- [ ] Custom domain configured
- [ ] SSL working (https://)
- [ ] Monitoring setup
- [ ] Billing alerts configured
- [ ] Backup plan documented

---

## 📞 Next Steps

1. **Deploy now:** https://railway.app
2. **Test the endpoints:** Use curl commands above
3. **Monitor performance:** Check Railway dashboard
4. **Add custom domain:** Optional but recommended
5. **Setup backups:** Railway handles this automatically

---

## 🎉 Success!

Your BetSystem AI is now **live in production** on Railway! 🚀

**URLs:**
- Frontend: `https://your-frontend.railway.app`
- Backend API: `https://your-backend.railway.app`
- API Docs: `https://your-backend.railway.app/docs`

**Cost:** Starting at $12-35/month (or $0 with free credits)

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
- PostgreSQL Docs: https://www.postgresql.org/docs

---

**Need help?** Check the logs or reach out to Railway support!
