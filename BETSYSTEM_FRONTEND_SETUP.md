# BetSystem AI - Frontend Setup Guide

## 🎉 Frontend Complete!

Your React frontend is ready to go. All files have been created in `/data/.openclaw/workspace/betsystem-ui/`

---

## 📁 Project Structure

```
betsystem-ui/
├── package.json           # Dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS config
├── postcss.config.js      # PostCSS config
├── index.html             # Entry HTML
├── src/
│   ├── main.jsx           # React entry point
│   ├── App.jsx            # Main app component
│   ├── index.css          # Global styles
│   ├── pages/
│   │   ├── Login.jsx      # Login page
│   │   ├── Dashboard.jsx  # Main dashboard
│   │   └── BetSuggestion.jsx  # Bet suggestion page
│   ├── components/
│   │   ├── Bankroll.jsx   # Bankroll display
│   │   └── BetHistory.jsx # Bet history table
│   └── api/
│       └── client.js      # API client
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- npm or yarn
- FastAPI backend running on http://localhost:8000

### Installation

```bash
cd /data/.openclaw/workspace/betsystem-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Open in Browser

Visit: **http://localhost:5173**

---

## 🔌 Backend Connection

The frontend connects to FastAPI at:
```
http://localhost:8000
```

**Make sure your FastAPI backend is running:**

```bash
cd /data/.openclaw/workspace
uvicorn betsystem_api:app --reload --port 8000
```

---

## 📋 Features Implemented

### ✅ Authentication
- Login page with username/password
- JWT token management
- Logout functionality

### ✅ Dashboard
- 4-tab navigation (Dashboard, Suggestions, History, Settings)
- Bankroll display cards
- Today's P&L, Win Rate, ROI
- Responsive grid layout

### ✅ Bet Suggestion Engine
- Match input form (team A, team B, odds, sport)
- API call to `/suggest-bet` endpoint
- Display suggestion with confidence, EV, recommended stake
- Risk level indicator
- Reasoning explanation

### ✅ Bet History
- Table showing past bets
- Win/Loss indicators
- P&L display
- Date tracking

### ✅ Responsive Design
- Mobile-friendly layout
- Tailwind CSS styling
- Dark theme (gray/blue palette)

### ✅ Error Handling
- API error messages
- Form validation
- Loading states

---

## 🎨 UI Components

### Login Page
- Email/password input
- Submit button with loading state
- Error display
- Responsive form

### Dashboard
- Header with logout button
- Tab navigation
- Bankroll card display
- Stats grid
- Disclaimer footer

### Bet Suggestion Form
- Sport selector (Football, Basketball, Tennis)
- Team A/B inputs
- Odds input
- Market input
- Date picker
- Submit button

### Suggestion Display
- Strategy name
- Confidence %
- Expected Value %
- Recommended stake
- Risk level badge
- Explanation list
- "Place Bet" button

### Bet History Table
- Sortable columns
- Win/Loss badges
- P&L color coding (green/red)
- Date display

---

## 🔌 API Integration

### Endpoints Connected

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/users/register` | POST | Create account |
| `/auth/login` | POST | Login user |
| `/bankroll/{user_id}` | GET | Fetch bankroll |
| `/suggest-bet/{user_id}` | POST | Get bet suggestion |
| `/bets/{user_id}` | POST | Place bet |
| `/bets/{user_id}` | GET | Get bet history |
| `/analytics/{user_id}/roi` | GET | Get ROI stats |

---

## 🧪 Testing the App

### Test Workflow

1. **Start FastAPI backend:**
```bash
cd /data/.openclaw/workspace
uvicorn betsystem_api:app --reload
```

2. **Start frontend dev server:**
```bash
cd /data/.openclaw/workspace/betsystem-ui
npm install
npm run dev
```

3. **Open browser:** http://localhost:5173

4. **Login:** Use test credentials (FastAPI creates demo users)

5. **Test bet suggestion:**
   - Click "Get Suggestion" tab
   - Fill in match details:
     - Team A: Arsenal
     - Team B: Liverpool
     - Odds: 1.92
     - Sport: Football
     - Market: Over 2.5 Goals
   - Click "Get Suggestion"

6. **View results:** See suggestion with confidence, EV, stake

---

## 📦 Build for Production

### Create Production Build

```bash
npm run build
```

Output goes to `dist/` folder

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts
```

### Deploy to Netlify

```bash
# Drag-and-drop dist/ folder to Netlify
# Or use Netlify CLI:
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

---

## 🛠️ Customization

### Change API URL

Edit `src/api/client.js`:

```javascript
const API_BASE_URL = process.env.VITE_API_URL || 'http://your-api.com:8000'
```

Or set environment variable:
```bash
VITE_API_URL=https://api.example.com npm run dev
```

### Change Theme Colors

Edit `tailwind.config.js` to customize colors:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
      secondary: '#your-color'
    }
  }
}
```

### Add New Pages

1. Create `src/pages/YourPage.jsx`
2. Import in `src/pages/Dashboard.jsx`
3. Add tab button to navigation
4. Add case in `currentPage` switch

---

## 📱 Mobile Responsive

The app is fully responsive:
- **Mobile:** Single column layout
- **Tablet:** 2-column grid
- **Desktop:** 3-4 column grid

Breakpoints:
- `md:` - 768px and above
- `lg:` - 1024px and above

---

## 🚀 Next Steps

### Phase 2 Features
- [ ] Advanced analytics charts (Chart.js)
- [ ] Multiple strategy selection UI
- [ ] Real-time odds integration
- [ ] Bet placement with confirmation
- [ ] Profit/loss charts
- [ ] Mobile app (React Native)
- [ ] Dark/light theme toggle
- [ ] Settings page

### Phase 3 Features
- [ ] WebSocket for real-time updates
- [ ] Email notifications
- [ ] Portfolio analysis
- [ ] Community leaderboards
- [ ] AI confidence training

---

## 📞 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 5173
lsof -i :5173
kill -9 <PID>

# Or use different port
npm run dev -- --port 3000
```

### CORS Issues

If you get CORS errors, make sure FastAPI backend has CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Backend Not Found

Make sure FastAPI is running:
```bash
uvicorn betsystem_api:app --reload --port 8000
```

### Dependencies Not Installing

```bash
# Clear cache
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

---

## 📚 Stack Info

- **Frontend:** React 18.2
- **Build Tool:** Vite 5.0
- **Styling:** Tailwind CSS 3.4
- **Routing:** React Router 6.2
- **HTTP Client:** Fetch API
- **State Management:** React Hooks

---

## 🎉 You're Ready!

The BetSystem AI frontend is complete and ready to:
1. ✅ Connect to your FastAPI backend
2. ✅ Display bet suggestions
3. ✅ Track betting performance
4. ✅ Manage bankroll
5. ✅ Provide educational betting analysis

**Start building!** 🚀
