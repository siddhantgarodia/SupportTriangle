# Vercel Deployment Guide

This guide walks you through deploying SupportTriangle to Vercel with proper security configuration.

## Prerequisites

- Vercel account (https://vercel.com)
- Git repository pushed to GitHub
- Groq API key from https://console.groq.com

## Step-by-Step Deployment

### 1. Generate JWT Secret

Generate a secure JWT secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Save this value — you'll need it in Step 4.

### 2. Create Vercel Project

```bash
npm install -g vercel
vercel link
```

Follow the prompts to create a new project or link to existing.

### 3. Set Environment Variables on Vercel

In your Vercel dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add the following variables:

| Variable Name | Value | Notes |
|---|---|---|
| `GROQ_API_KEY` | `gsk_...` | Get from https://console.groq.com |
| `JWT_SECRET` | Your generated secret | Use 32+ character secret |
| `ALLOWED_ORIGINS` | `https://your-domain.vercel.app` | Full HTTPS URL of your deployment |
| `SYNC_TICKET_PROCESSING` | `true` | Required for Vercel serverless |

### 4. Deploy

```bash
vercel deploy --prod
```

Or push to GitHub and enable auto-deployment in Vercel dashboard.

## Security Checklist

Before going to production:

- [ ] `GROQ_API_KEY` is set (not empty)
- [ ] `JWT_SECRET` is at least 32 characters
- [ ] `ALLOWED_ORIGINS` is set to your actual domain (not `*`)
- [ ] `.env` file is in `.gitignore` (never committed)
- [ ] `vercel.json` uses `experimentalServices` configuration
- [ ] All environment variables are set on Vercel Dashboard (not hardcoded)

## Monitoring

After deployment, monitor the logs:

```bash
vercel logs --follow
```

Look for:
- Startup errors about missing environment variables
- Rate limit warnings (429 status codes)
- LLM pipeline errors

## Troubleshooting

### "GROQ_API_KEY not set"

**Solution:** 
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add `GROQ_API_KEY` with your actual key
3. Redeploy: `vercel deploy --prod`

### "JWT_SECRET is required and must be at least 32 characters"

**Solution:**
1. Generate a new secret: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Add to Vercel Dashboard with key `JWT_SECRET`
3. Redeploy

### CORS errors in browser console

**Solution:**
1. Check that `ALLOWED_ORIGINS` matches your Vercel deployment URL
2. URL must be `https://your-project.vercel.app` (exact match)
3. Redeploy after updating

### Rate limit errors (429)

**Solution:**
- Free Groq API has ~30 requests/minute limit
- Implementation respects this with `GROQ_INTER_CALL_DELAY_SEC`
- Consider upgrading Groq plan for higher limits

## Local Testing Before Deployment

To test the exact Vercel environment locally:

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with actual values
# Set SYNC_TICKET_PROCESSING=true to match Vercel

# Run backend
cd backend
pip install -r requirements.txt
SYNC_TICKET_PROCESSING=true python -m uvicorn main:app --reload

# In another terminal, run frontend
cd frontend
npm install
npm run dev
```

## Database Persistence

SQLite is stored in Vercel's `/tmp` directory, which is ephemeral (cleared between deployments).

**For production with persistent data:**

Consider migrating to PostgreSQL:
- Use Vercel's Postgres integration
- Update connection string in `config.py`
- Update `db.py` to use `psycopg2` driver

## Support

- Groq API docs: https://console.groq.com/docs
- Vercel docs: https://vercel.com/docs
- FastAPI docs: https://fastapi.tiangolo.com/
