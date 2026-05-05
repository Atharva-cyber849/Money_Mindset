# Deployment Guide

This project is deployed as two separate applications:

- Frontend: Next.js on Vercel
- Backend: FastAPI on Render

This split is the recommended setup for production because it lets each part scale and deploy independently.

## 1. Frontend Deployment On Vercel

### 1.1 Prerequisites

- Push the frontend-only repository to GitHub.
- Make sure the backend is already deployed and has a public URL.

### 1.2 Create The Vercel Project

1. Open Vercel and click **New Project**.
2. Import the frontend repository.
3. Set the **Root Directory** to the frontend project folder if needed.
4. Let Vercel detect the framework as **Next.js**.

### 1.3 Build Settings

Use these settings:

- Build Command: `npm run build`
- Install Command: `npm install`
- Output Directory: leave default

### 1.4 Environment Variables

Add this environment variable in Vercel:

- `NEXT_PUBLIC_API_URL` = `https://your-backend-domain/api/v1`

Example:

```env
NEXT_PUBLIC_API_URL=https://money-mindset-backend.onrender.com/api/v1
```

### 1.5 Deploy

1. Click **Deploy** in Vercel.
2. Wait for the production build to finish.
3. Open the deployed frontend URL and test login, dashboards, and analytics pages.

### 1.6 Frontend Verification

Check these pages after deployment:

- Dashboard
- Analytics pages
- Games pages
- Login / Register

If API calls fail, confirm the backend URL and CORS settings.

## 2. Backend Deployment On Render

### 2.1 Prerequisites

- Push the backend-only repository to GitHub.
- Create a Postgres database in Render.

### 2.2 Create The Render Web Service

1. Open Render and click **New Web Service**.
2. Import the backend repository.
3. Set the **Root Directory** to `backend` if required.
4. Use the settings from [render.yaml](render.yaml).

Recommended values:

- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

### 2.3 Database Setup

1. Create a Render Postgres database.
2. Copy the database connection string.
3. Add it as `DATABASE_URL` in the Render web service environment variables.

### 2.4 Backend Environment Variables

Set these variables in Render:

```env
DEBUG=False
APP_NAME=Money Mindset API
VERSION=1.0.0
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-render-postgres-url
CORS_ORIGINS=["https://your-frontend-domain.vercel.app","http://localhost:3000"]
```

Optional variables if you use those features:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`
- `ANTHROPIC_API_KEY`
- `FINNHUB_API_KEY`
- `NEWSAPI_KEY`

Optional preview-domain support:

```env
CORS_ALLOW_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

### 2.5 Deploy

1. Click **Deploy** in Render.
2. Wait for the service to become healthy.
3. Open `/health` to confirm the API is running.
4. Open `/docs` to confirm the endpoints are available.

### 2.6 Backend Verification

Test these endpoints after deployment:

- `/health`
- `/docs`
- `/api/v1/auth`
- `/api/v1/transactions`
- `/api/v1/analytics`

If the frontend cannot call the backend, check CORS and the frontend API URL.

## 3. Recommended Deployment Order

1. Deploy the backend first.
2. Copy the backend URL.
3. Set `NEXT_PUBLIC_API_URL` in Vercel.
4. Deploy the frontend.
5. Test authentication and API flows.

## 4. Final Production Checklist

- Frontend repo pushed and deployed on Vercel
- Backend repo pushed and deployed on Render
- Render Postgres connected
- `NEXT_PUBLIC_API_URL` set correctly in Vercel
- `CORS_ORIGINS` set correctly in backend
- `CORS_ALLOW_ORIGIN_REGEX` set if using Vercel previews
- `/health` returns healthy
- Login and analytics pages work in production

## 5. Useful Repository Links

- Frontend repo: `https://github.com/Atharva-cyber849/Money-Minset-Frontend`
- Backend repo: `https://github.com/Atharva-cyber849/Money-Mindset-Backend`
