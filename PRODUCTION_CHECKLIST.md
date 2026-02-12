# BetSystem AI - Production Deployment Checklist

---

## 📋 Pre-Deployment (Day Before)

- [ ] **Code Review**
  - [ ] All features tested locally
  - [ ] No console errors
  - [ ] API endpoints verified
  - [ ] Database migrations tested

- [ ] **Security Audit**
  - [ ] No hardcoded secrets in code
  - [ ] .env.production file created
  - [ ] API keys secured
  - [ ] CORS settings reviewed

- [ ] **Infrastructure Setup**
  - [ ] Server/VPS prepared
  - [ ] Docker & Docker Compose installed
  - [ ] Database setup (PostgreSQL or Supabase)
  - [ ] Backups configured
  - [ ] DNS records ready

- [ ] **Documentation**
  - [ ] Deployment guide reviewed
  - [ ] Runbook prepared
  - [ ] Rollback plan documented
  - [ ] Contact list updated

---

## 🚀 Deployment Day (Go-Live)

### Hour -1: Final Checks

- [ ] **Staging Test**
  ```bash
  docker-compose up -d
  curl http://localhost:3000
  curl http://localhost:8000
  ```
  All services healthy? ✅

- [ ] **Database**
  ```bash
  psql $DATABASE_URL -c "SELECT 1"
  ```
  Connection working? ✅

- [ ] **Git Status**
  ```bash
  git status
  git log --oneline -5
  ```
  All changes committed? ✅

- [ ] **Backup**
  ```bash
  # Backup current database
  pg_dump $DATABASE_URL > backup.sql
  ```
  Backup complete? ✅

### Hour 0: Deployment

- [ ] **Stop Staging Services**
  ```bash
  docker-compose down
  ```

- [ ] **Build Production Images**
  ```bash
  docker build -t betsystem-backend:v1.0.0 .
  docker build -t betsystem-frontend:v1.0.0 ./betsystem-ui
  ```

- [ ] **Update Environment Variables**
  ```bash
  # Copy .env.example to .env
  cp .env.example .env
  # Edit with production values
  nano .env
  ```

- [ ] **Start Services**
  ```bash
  docker-compose up -d
  # Wait 30 seconds for services to initialize
  sleep 30
  ```

- [ ] **Verify Health**
  ```bash
  # Backend
  curl -v http://localhost:8000/
  
  # Frontend
  curl -v http://localhost:3000
  
  # Logs
  docker-compose logs backend | tail -20
  docker-compose logs frontend | tail -20
  ```

- [ ] **API Documentation**
  ```bash
  curl http://localhost:8000/docs
  ```
  Swagger UI accessible? ✅

### Hour 1: Live Testing

- [ ] **Functional Tests**
  - [ ] Login works
  - [ ] Dashboard loads
  - [ ] Bankroll displays correctly
  - [ ] Bet suggestion generates
  - [ ] Bet placement works
  - [ ] History table shows data

- [ ] **API Tests**
  ```bash
  # Register user
  curl -X POST http://localhost:8000/users/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test","username":"test"}'
  
  # Get user
  curl http://localhost:8000/users/user_id
  ```

- [ ] **Performance Tests**
  - [ ] Page load time < 3s
  - [ ] API response time < 500ms
  - [ ] No memory leaks
  - [ ] Database queries optimized

- [ ] **Error Handling**
  - [ ] Invalid API calls return proper errors
  - [ ] Database errors logged
  - [ ] Frontend error boundaries working
  - [ ] 404/500 pages configured

---

## 🌐 DNS & Domain Configuration

- [ ] **Domain Setup**
  ```bash
  # Update DNS records
  A Record: yourdomain.com → server-ip
  CNAME: api.yourdomain.com → backend-url
  ```

- [ ] **SSL/HTTPS**
  - [ ] Certificate installed
  - [ ] HTTPS working
  - [ ] HTTP redirects to HTTPS
  - [ ] SSL/TLS test passed

- [ ] **CDN (Optional)**
  - [ ] CloudFlare configured
  - [ ] Cache rules set
  - [ ] Rate limiting enabled

---

## 🔐 Security Verification

- [ ] **API Security**
  ```bash
  # Test CORS
  curl -H "Origin: https://yourdomain.com" \
    -H "Access-Control-Request-Method: POST" \
    -X OPTIONS http://localhost:8000/
  ```
  Returns 200? ✅

- [ ] **Authentication**
  - [ ] Tokens expiring correctly
  - [ ] Passwords hashed
  - [ ] Session management working

- [ ] **Database Security**
  - [ ] SQL injection protected
  - [ ] Backups encrypted
  - [ ] Access restricted

- [ ] **Secret Management**
  - [ ] No secrets in git
  - [ ] .env in .gitignore
  - [ ] Environment variables set

---

## 📊 Monitoring & Logging

- [ ] **Logging Setup**
  ```bash
  # Tail logs in real-time
  docker-compose logs -f backend
  docker-compose logs -f frontend
  ```

- [ ] **Error Tracking**
  - [ ] Error logs going to file
  - [ ] Critical errors alerting
  - [ ] Email notifications working

- [ ] **Performance Monitoring**
  - [ ] Response time metrics
  - [ ] Database query logs
  - [ ] API endpoint metrics

- [ ] **Uptime Monitoring** (Optional)
  - [ ] Ping monitor configured
  - [ ] Alerts set up
  - [ ] Status page created

---

## 🔄 Rollback Preparation

- [ ] **Previous Version Tagged**
  ```bash
  docker tag betsystem-backend:v1.0.0 betsystem-backend:latest
  ```

- [ ] **Rollback Script**
  ```bash
  #!/bin/bash
  # rollback.sh
  docker-compose down
  docker pull betsystem-backend:v0.9.9
  docker-compose up -d
  ```

- [ ] **Database Rollback Plan**
  - [ ] Backup location known
  - [ ] Restore procedure tested
  - [ ] Time to restore < 30 minutes

---

## ✅ Post-Deployment (Hour 2-4)

### Monitoring Phase

- [ ] **Live Traffic Observation**
  - [ ] Error rates normal
  - [ ] Response times acceptable
  - [ ] No database issues
  - [ ] API capacity sufficient

- [ ] **User Testing**
  - [ ] Test users can login
  - [ ] Dashboard loads
  - [ ] Trading features work
  - [ ] No crashes

- [ ] **Data Verification**
  ```bash
  psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
  psql $DATABASE_URL -c "SELECT COUNT(*) FROM bets;"
  ```
  Data intact? ✅

### Performance Baseline

- [ ] **Record Metrics**
  - [ ] Page load time: _____ ms
  - [ ] API response time: _____ ms
  - [ ] Error rate: _____ %
  - [ ] CPU usage: _____ %
  - [ ] Memory usage: _____ MB

- [ ] **Compare to Expectations**
  - [ ] Within SLA?
  - [ ] Better than staging?
  - [ ] Acceptable for users?

---

## 📞 Incident Response

### If Something Goes Wrong

1. **STOP:** Don't panic
2. **ASSESS:** Check logs and errors
3. **COMMUNICATE:** Notify team
4. **ROLLBACK:** Revert to previous version if needed
5. **INVESTIGATE:** Find root cause
6. **FIX:** Update code/config
7. **RETEST:** Verify fix in staging
8. **REDEPLOY:** Go live again

### Rollback Decision Tree

```
Error severity?
├─ Critical (API down) → Rollback immediately
├─ High (Features broken) → Investigate for 15 min, then rollback if unresolved
├─ Medium (Performance degraded) → Investigate, fix, redeploy
└─ Low (Minor issues) → Schedule fix for next release
```

---

## 📝 Sign-Off

- [ ] **Deployment Lead:** _________________ Date: _________
- [ ] **QA Lead:** _________________ Date: _________
- [ ] **DevOps:** _________________ Date: _________
- [ ] **Project Manager:** _________________ Date: _________

**All Sign-Offs Complete → DEPLOYMENT SUCCESS** ✅

---

## 📋 Post-Deployment Maintenance

### Daily (Next 7 days)
- [ ] Monitor error rates
- [ ] Check database performance
- [ ] Verify backups running
- [ ] Review user feedback

### Weekly (First Month)
- [ ] Performance review
- [ ] Security audit
- [ ] Database optimization
- [ ] Code deployment pipeline test

### Monthly
- [ ] Infrastructure review
- [ ] Capacity planning
- [ ] Dependency updates
- [ ] Disaster recovery drill

---

**Deployment Date:** _______________  
**Deployment Duration:** _______________  
**Issues Encountered:** _______________  
**Resolution Time:** _______________  
**Notes:** _________________________________________________

---

🎉 **Congratulations! BetSystem AI is now live in production!**
