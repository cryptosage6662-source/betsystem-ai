# BetSystem AI - Production Deployment Guide

**Status:** Ready for Production  
**Last Updated:** 2026-02-12  
**Version:** 1.0.0

---

## 🚀 Quick Start (5 minutes)

### Option 1: Local Docker (Development)

```bash
# Build and run locally
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Option 2: Cloud Deployment (Production)

---

## 📋 Pre-Deployment Checklist

- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Git repository initialized
- [ ] Environment variables configured
- [ ] Database backup plan
- [ ] Monitoring setup planned

---

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │  Port 3000
│  (Vite + Serve) │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│  FastAPI Backend│  Port 8000
│  (Uvicorn)      │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│   Database      │
│ (SQLite/PgSQL)  │
└─────────────────┘
```

---

## 🐳 Docker Deployment

### Build Images

```bash
# Build backend
docker build -t betsystem-backend:latest .

# Build frontend
docker build -t betsystem-frontend:latest ./betsystem-ui
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

### Verify Services

```bash
# Check backend health
curl http://localhost:8000/

# Check frontend
curl http://localhost:3000

# View running containers
docker ps
```

---

## ☁️ Cloud Deployment Options

### Option A: Railway.app (Recommended)

**Setup:**

1. **Create Railway account:** https://railway.app
2. **Connect GitHub repo** (or manual deploy)
3. **Create Backend Service:**
   ```
   - Build: Dockerfile
   - Start Command: uvicorn betsystem_api:app --host 0.0.0.0 --port 8000
   - Environment: DATABASE_URL, DEBUG=False
   ```
4. **Create Frontend Service:**
   ```
   - Build: betsystem-ui/Dockerfile
   - Start Command: serve -s dist -l 3000
   ```
5. **Deploy**

**Result:** Public URLs
```
Backend: https://your-backend.railway.app
Frontend: https://your-frontend.railway.app
```

### Option B: Heroku

**Setup:**

1. **Create Heroku account:** https://heroku.com
2. **Install Heroku CLI:** `brew install heroku`
3. **Login:** `heroku login`
4. **Create apps:**
   ```bash
   heroku create your-app-backend
   heroku create your-app-frontend
   ```
5. **Deploy:**
   ```bash
   # Backend
   git subtree push --prefix . heroku main

   # Frontend
   cd betsystem-ui
   git subtree push --prefix betsystem-ui heroku main
   ```

### Option C: AWS (EC2 + RDS)

**Setup:**

1. **Launch EC2 instance** (Ubuntu 22.04 LTS)
2. **Install Docker & Docker Compose**
3. **Clone repo & deploy:**
   ```bash
   docker-compose up -d
   ```
4. **Configure RDS** for PostgreSQL
5. **Setup Nginx** as reverse proxy
6. **Get SSL certificate** (Let's Encrypt)

---

## 🗄️ Database Setup

### SQLite (Development)

```bash
# Already configured in docker-compose.yml
# Auto-initialized on first run
```

### PostgreSQL (Production)

**Option 1: Supabase (Recommended)**

1. Create account: https://supabase.com
2. Create new project
3. Get connection string
4. Update `DATABASE_URL` environment variable

**Option 2: AWS RDS**

1. Create RDS PostgreSQL instance
2. Get endpoint
3. Update environment variables

**Migration:**

```bash
# Update betsystem_api.py
# Change: sqlite:///./betsystem.db
# To: postgresql://user:pass@host:5432/betsystem

python -m alembic upgrade head
```

---

## 🔐 Security Configuration

### Environment Variables (.env.production)

```env
# Backend
DEBUG=False
DATABASE_URL=postgresql://user:pass@host/betsystem
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,*.yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

### API Security

```python
# Added to betsystem_api.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Production domain only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSL/HTTPS

**Nginx + Let's Encrypt:**

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Monitoring & Logging

### Application Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Persistent logs
docker-compose logs --timestamps backend > backend.log
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/

# Frontend health
curl https://yourdomain.com/

# API docs
curl https://api.yourdomain.com/docs
```

### Performance Monitoring

- **Application:** Sentry (optional setup)
- **Infrastructure:** Datadog (optional setup)
- **Database:** PostgreSQL monitoring

---

## 🚨 Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port 8000 already in use
# - Database connection failed
# - Missing dependencies

# Solution:
docker-compose restart backend
```

### Frontend Blank Page

```bash
# Check frontend logs
docker-compose logs frontend

# Common issues:
# - API URL misconfigured
# - Build failed
# - CORS blocked

# Solution:
docker-compose restart frontend
```

### Database Connection Failed

```bash
# Verify connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Update docker-compose.yml if needed
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml - Add replicas
services:
  backend:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing

Use Nginx reverse proxy:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

---

## 🔄 Continuous Deployment (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        run: |
          docker build -t betsystem-backend:latest .
          docker build -t betsystem-frontend:latest ./betsystem-ui
      - name: Deploy to Railway
        run: railway up
```

---

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrated to production
- [ ] SSL/HTTPS certificates installed
- [ ] Domain DNS configured
- [ ] Monitoring and logging setup
- [ ] Backup strategy configured
- [ ] Rate limiting enabled
- [ ] CORS configured for production domain
- [ ] API documentation accessible
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Rollback plan documented

---

## 🚀 Go Live

### 1. Final Testing

```bash
# Test all endpoints
curl https://api.yourdomain.com/
curl https://yourdomain.com

# Verify database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"

# Check logs
docker-compose logs backend | tail -20
```

### 2. Update DNS

```
A Record: yourdomain.com → your-server-ip
CNAME: api.yourdomain.com → your-api-url
```

### 3. Monitor

```bash
# Watch logs during first hour
docker-compose logs -f

# Check error rates
# Monitor database queries
# Verify SSL certificate
```

---

## 📞 Post-Deployment

### Maintenance

- Daily: Check logs, monitor errors
- Weekly: Review performance metrics
- Monthly: Database maintenance, security updates
- Quarterly: Performance optimization, code updates

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d

# Verify health
curl https://yourdomain.com/health
```

---

## 🆘 Support & Rollback

### Rollback Procedure

```bash
# Keep previous version tagged
docker tag betsystem-backend:latest betsystem-backend:v1.0.0

# On failure, revert
docker-compose down
docker pull betsystem-backend:v1.0.0
docker-compose up -d
```

### Contact Support

- Email: support@yourdomain.com
- Docs: https://yourdomain.com/docs
- Status Page: https://status.yourdomain.com

---

**Deployment Complete! 🎉**

Your BetSystem AI is now production-ready!
