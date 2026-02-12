---
summary: "Workspace template for TOOLS.md"
read_when:
  - Bootstrapping a workspace manually
---

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## Token Optimization Setup (2026-02-11)

### Ollama Configuration
- **Status:** Installing (brew install ollama)
- **Model:** llama2:7b (for heartbeats)
- **Endpoint:** http://localhost:11434
- **Usage:** Free local LLM for heartbeat checks (eliminates $5-15/month in API costs)
- **Start command:** `ollama serve` (background)

### Model Routing
- **Primary:** Haiku (anthropic/claude-haiku-4-5) — Default for all routine work
- **Premium:** Sonnet (anthropic/claude-sonnet-4-5) — Only for complex reasoning
- **Cost savings:** ~$45-60/month by routing 90% of work to Haiku

### Cost Tracking
- **Daily budget:** $5
- **Monthly budget:** $200
- **Current monthly baseline:** $30-50 (after optimizations)
- **Previous baseline:** $1,500+ (unoptimized)

---

Add whatever helps you do your job. This is your cheat sheet.