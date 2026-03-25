# TradeIQ Deployment Guide (Render + Vercel)

This setup deploys:
- Django backend on Render
- React (Vite) frontend on Vercel

## 1. Push Project to GitHub

From project root:

```powershell
cd e:\TredalQ
git init
git add .
git commit -m "Prepare TradeIQ for deployment"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 2. Deploy Backend on Render

1. Open Render dashboard.
2. Create a new PostgreSQL database.
3. Create a new Web Service from your GitHub repo.
4. Configure service:
- Root Directory: `tradeiq_backend`
- Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Start Command: `gunicorn tradeiq_backend.wsgi:application`

5. Add environment variables in Render Web Service:
- `DEBUG=False`
- `SECRET_KEY=<generate-a-strong-random-secret>`
- `ALLOWED_HOSTS=<your-render-service>.onrender.com`
- `CORS_ALLOWED_ORIGINS=https://<your-vercel-domain>.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://<your-render-service>.onrender.com,https://<your-vercel-domain>.vercel.app`
- `DATABASE_URL=<Render PostgreSQL Internal Database URL>`

Note: Backend automatically parses `DATABASE_URL` for PostgreSQL.

6. Deploy and wait for build to complete.
7. Verify health endpoint:
- `https://<your-render-service>.onrender.com/api/health/`

## 3. Deploy Frontend on Vercel

1. Open Vercel dashboard.
2. Import same GitHub repository.
3. Set project root to `tradeiq_frontend`.
4. Build settings:
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`

5. Add environment variable:
- `VITE_API_BASE_URL=https://<your-render-service>.onrender.com/api`

6. Deploy.

## 4. Update Backend CORS (if frontend domain changed)

If Vercel gives a different production domain, update Render env:
- `CORS_ALLOWED_ORIGINS=https://<actual-vercel-domain>`
- `CSRF_TRUSTED_ORIGINS=https://<your-render-service>.onrender.com,https://<actual-vercel-domain>`

Then redeploy backend.

## 5. Post-Deploy Checks

1. Frontend opens: `https://<your-vercel-domain>.vercel.app`
2. Login/register works.
3. Stock lookup endpoint works.
4. Prediction endpoint returns response.
5. No CORS errors in browser console.

## 6. Common Fixes

- 502/500 on backend start:
  - Check Render logs for missing env vars or migration issues.
- CORS blocked:
  - Verify exact frontend URL in `CORS_ALLOWED_ORIGINS`.
- Static files missing:
  - Ensure `collectstatic --noinput` ran in build command.
- Database errors:
  - Verify `DATABASE_URL` points to active Render PostgreSQL instance.

## 7. Optional: One-Command Local Production Smoke Test

Backend:

```powershell
cd e:\TredalQ\tradeiq_backend
$env:DEBUG="False"
$env:ALLOWED_HOSTS="127.0.0.1,localhost"
python manage.py check --deploy
```

Frontend build:

```powershell
cd e:\TredalQ\tradeiq_frontend
npm run build
```
