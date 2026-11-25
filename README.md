---
title: AI SupportOps
emoji: 🎧
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# AI SupportOps

An AI-powered customer support platform built with React, FastAPI, LangGraph, Groq, Supabase PostgreSQL/pgvector, role-based access, multilingual tickets, human approval workflows, and Cactus Mirage image understanding.

## Deployment architecture

This Space builds the React/Vite frontend and serves it from the FastAPI application in one Docker container. The browser and API therefore use the same HTTPS origin.

Persistent application records, tickets, users, approvals, knowledge-base chunks and embeddings are stored in the configured external PostgreSQL database. Do not use SQLite or container-local files as production storage.

## Required Space secrets

Add these under **Space Settings → Variables and secrets → Secrets**:

- `DATABASE_URL`: PostgreSQL connection string for the existing Supabase database. Use the SQLAlchemy psycopg URL format, for example `postgresql+psycopg://...`.
- `JWT_SECRET_KEY`: a unique random value of at least 32 characters.
- `GROQ_API_KEY`: your Groq API key.

## Runtime variables

Add these under **Space Settings → Variables and secrets → Variables**:

- `ENVIRONMENT=production`
- `LLM_PROVIDER=groq`
- `GROQ_MODEL=openai/gpt-oss-20b`
- `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `MAX_VISION_UPLOAD_MB=8`
- `EMBEDDING_MODEL=BAAI/bge-small-en-v1.5`
- `EMBEDDING_DIMENSION=384`

The frontend is served from the same origin as FastAPI, so do not set `VITE_API_BASE_URL` to localhost in the Space.

## Database setup

Use the existing Supabase database and its already-applied schema migration. If deploying against a new database, enable the pgvector extension and create the application's tables before using the knowledge-base feature. Provision the initial administrator against that same database before public use.

## Notes

- The Space's local filesystem is not durable across restarts. The application uses Supabase PostgreSQL for persistent records and embeddings.
- Cactus Mirage runs inside the Docker container and downloads its runtime/model the first time vision analysis is used. Validate a real image inference on the selected Space hardware; the CPU Basic tier may be slower than a dedicated GPU.
- Free CPU hardware sleeps after inactivity. First requests after a sleep or restart may take longer.
- Never put database passwords, JWT secrets or API keys in this repository.
