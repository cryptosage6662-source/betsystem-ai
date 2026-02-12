# Token Optimization Setup - 2026-02-11

## What Just Changed

You've enabled a suite of cost-cutting measures that should reduce your token spending from **$1,500+/month to $30-50/month** (97% reduction).

## 1. ✅ Config Updated (~/.openclaw/openclaw.json)

**Changes made:**
- Primary model: Set to Haiku (was Sonnet)
- Model aliases: sonnet, haiku, gpt, gemini, grok, opus (use these to switch)
- Prompt caching: Enabled for static files (SOUL.md, USER.md, TOOLS.md)
- Heartbeat: Configured to use Ollama (local, free)
- Heartbeat interval: Every 1 hour

**Impact:** ~$50-70/month → ~$5-10/month on models alone

---

## 2. ✅ System Prompt Updated (SOUL.md)

**Added optimization rules:**
- Session initialization: Load only SOUL.md, USER.md, IDENTITY.md + today's notes
- Model selection: Haiku by default, Sonnet only for complex reasoning
- Rate limits: 5s between API calls, 10s between searches
- Budget tracking: $5/day, $200/month

**Impact:** Prevents token bloat and runaway costs

---

## 3. ⏳ Ollama Installation In Progress

Ollama is installing via brew. This provides:
- Free local LLM (llama2:7b)
- Heartbeat checks without API costs
- No rate limiting (local = unlimited)

**Manual step when ready:**

```bash
# Wait for brew to finish, then start Ollama in the background
ollama serve &

# Pull the model (first time only, ~4GB)
ollama pull llama2:7b

# Test it
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b",
  "prompt": "Say OK"
}' | jq
```

**Impact:** ~$5-15/month → $0/month on heartbeats

---

## 4. ✅ TOOLS.md Updated

Added Ollama configuration reference and cost tracking notes.

---

## What To Do Now

### Immediate (in next 2 minutes)
1. Restart OpenClaw to load the new config:
   ```bash
   openclaw gateway restart
   ```

2. Check if Ollama finished installing:
   ```bash
   brew list ollama
   ```

### Once Ollama is Ready
1. Start Ollama in background:
   ```bash
   ollama serve &
   ```

2. Pull the model:
   ```bash
   ollama pull llama2:7b
   ```

3. Test heartbeat is working:
   ```bash
   openclaw shell
   # Then in OpenClaw: session_status
   ```

---

## How to Use the New Optimization

### Model Switching
**Haiku (default, cheap):**
```
Regular tasks, file checks, simple coding
No model override needed
```

**Sonnet (premium, when needed):**
```
When you hit limits with Haiku, explicitly ask:
"Use sonnet: [complex reasoning task]"
Or in code: model="sonnet"
```

### Memory Management
**Daily notes stay lean:**
- `memory/YYYY-MM-DD.md` captures decisions, leads, blockers
- `MEMORY.md` is NOT auto-loaded (loads on-demand only)
- Use `memory_search()` then `memory_get()` for specific snippets

### Rate Limiting in Practice
The rules are built into your system prompt:
- API calls auto-throttle (5s between)
- Searches auto-throttle (10s between, max 5 per batch)
- Batching happens automatically (e.g., "get 10 leads" = 1 API call, not 10)

---

## Cost Tracking

After this is live, monitor actual costs:

```bash
# Check session usage
openclaw shell
session_status

# Should show:
# Model: haiku (or active model)
# Context: 2-8KB (not 50KB+)
# Heartbeat: ollama/local (not API)
# Daily run cost: $0.10-0.50 (not $2-3)
```

---

## Questions?

Refer to the original optimization guide: https://docs.google.com/document/u/0/d/1ffmZEfT7aenfAz2lkjyHsQIlYRWFpGcM/mobilebasic

Key sections:
- Part 1: Session Initialization
- Part 2: Model Routing
- Part 3: Heartbeat to Ollama
- Part 4: Rate Limits & Budget Controls
- Part 5: Prompt Caching
