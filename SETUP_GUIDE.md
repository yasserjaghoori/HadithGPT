# HadithGPT Setup Guide - Phase 2

Complete setup guide for HadithGPT with Supabase integration.

## Prerequisites

- Python 3.11+
- OpenAI API key
- Pinecone account
- Supabase account (free tier works!)

## Step 1: Rotate Compromised API Keys

**⚠️ URGENT**: Your API keys were exposed. Rotate them immediately:

1. **OpenAI**:
   - Go to https://platform.openai.com/api-keys
   - Find the exposed key (starts with `sk-proj-HsAv1...`)
   - Click "Revoke" or delete it
   - Create a new key

2. **Pinecone**:
   - Go to https://app.pinecone.io/
   - Navigate to API Keys
   - Regenerate your API key

## Step 2: Set Up Supabase

### Create Supabase Project

1. Go to https://supabase.com
2. Click "Start your project"
3. Create new organization (if needed)
4. Create new project:
   - Name: `hadithgpt`
   - Database Password: (generate strong password)
   - Region: Choose closest to you
   - Wait ~2 minutes for setup

### Get Supabase Credentials

1. In your Supabase project dashboard:
2. Go to **Settings** → **API**
3. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

### Set Up Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `database/schema.sql`
4. Paste and click **Run**
5. You should see: "Success. No rows returned"

This creates:
- `user_profiles` table
- `conversations` table
- `messages` table
- `query_history` table
- All necessary indexes and security policies

## Step 3: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your favorite editor
```

Add your credentials:

```env
# OpenAI (NEW key after rotation!)
OPENAI_API_KEY=sk-proj-YOUR_NEW_KEY_HERE

# Pinecone (NEW key after rotation!)
PINECONE_API_KEY=pcsk_YOUR_NEW_KEY_HERE

# Supabase
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...YOUR_ANON_KEY_HERE
```

**Important**: Never commit `.env` to Git!

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (API server)
- OpenAI (embeddings & LLM)
- Pinecone (vector search)
- Supabase (database & auth)
- All utilities

## Step 5: Run the API

### Development Mode

```bash
cd api
python -m uvicorn main:app --reload --port 8000
```

Visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Production Mode (Docker)

```bash
docker-compose up --build
```

## Step 6: Test the Setup

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy", "timestamp": "..."}`

### Test 2: Get Collections

```bash
curl http://localhost:8000/collections
```

Expected: List of your hadith collections

### Test 3: Search (No Auth Required)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What did the Prophet say about prayer?", "top_k": 3}'
```

Expected: JSON with search results

### Test 4: Run Test Suite

```bash
python test_api.py
```

## Phase 2 Features

### What's New?

1. **Supabase Integration**
   - PostgreSQL database for user data
   - Row-level security (RLS) enabled
   - Automatic profile creation on signup

2. **Database Models**
   - User Profiles
   - Conversations (chat sessions)
   - Messages (individual queries/responses)
   - Query History (for analytics)

3. **Authentication Ready**
   - Supabase Auth integration
   - JWT token validation
   - Optional vs required auth

4. **Conversation Memory**
   - Store user queries
   - Track conversation context
   - Enable follow-up questions

## Next Steps

### For Production:

1. **Add Authentication Endpoints** (Phase 2 next)
   - `/auth/signup`
   - `/auth/login`
   - `/auth/logout`

2. **Add Conversation Endpoints**
   - `POST /conversations` - Create conversation
   - `GET /conversations` - List user conversations
   - `GET /conversations/{id}/messages` - Get conversation history
   - `POST /conversations/{id}/messages` - Add message

3. **Enhance Search with Context**
   - Use previous messages in conversation
   - Personalize based on user preferences
   - Remember user's favorite collections

4. **Deploy to Production**
   - Railway / Render / Vercel
   - Set environment variables
   - Enable HTTPS

## Troubleshooting

### "Supabase not initialized"

- Check `.env` has correct `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Restart the API server

### "No collections found"

- Run `python embed_hadiths.py YourCollection.jsonl`
- Verify Pinecone API key is correct

### "Authentication failed"

- Ensure you're using the Supabase anon key (not service key)
- Check JWT token is valid

### Database errors

- Verify schema was applied correctly in Supabase SQL Editor
- Check RLS policies are enabled

## Architecture Overview

```
┌─────────────┐
│   Frontend  │ (Next.js - coming in Phase 3)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │  Auth    │  │ Database │           │
│  │ Middleware│  │  Layer   │           │
│  └────┬─────┘  └────┬─────┘           │
│       │             │                  │
│  ┌────▼─────────────▼─────┐           │
│  │   Search Logic          │           │
│  │ - Query Classification  │           │
│  │ - Query Enhancement     │           │
│  │ - Embedding Creation    │           │
│  └──────────┬──────────────┘           │
└─────────────┼──────────────────────────┘
              │
        ┌─────┴─────┐
        │           │
   ┌────▼────┐ ┌───▼────┐
   │Supabase │ │Pinecone│
   │         │ │        │
   │- Users  │ │- Hadith│
   │- Convos │ │ Vectors│
   │- Msgs   │ │        │
   └─────────┘ └────────┘
```

## Security Checklist

- [ ] Rotated compromised API keys
- [ ] `.env` is in `.gitignore`
- [ ] Never commit API keys to Git
- [ ] Supabase RLS policies enabled
- [ ] Using anon key (not service key) in frontend
- [ ] HTTPS enabled in production
- [ ] CORS configured for your domain only

## Support

Questions? Issues?
- Check logs: API outputs detailed error messages
- Supabase dashboard: Monitor database in real-time
- Test with Postman/Insomnia for debugging

Good luck! 🚀
