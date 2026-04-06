=================================================================
  LENDLYFIN — COMPLETE DEPLOYMENT GUIDE
  GitHub → Netlify (frontend) + Render (backend)
  Estimated time: 30–45 minutes
=================================================================

Your stack:
  FRONTEND  → Netlify  (free, auto-deploys from GitHub)
  BACKEND   → Render   (free, FastAPI + Python)
  DATABASE  → Neon     (free PostgreSQL, forever)
  REPO      → GitHub   github.com/av72245/lendlyfin


=================================================================
 STEP 1 — PUSH TO GITHUB  (run in your Terminal)
=================================================================

Open Terminal, go to your lendlyfin folder, then run:

  cd ~/Downloads/lendlyfin

  git init
  git branch -M main
  git add .
  git commit -m "Initial commit — Lendlyfin"

Now create the GitHub repository:
  1. Go to:  https://github.com/new
  2. Repository name: lendlyfin
  3. Set to: Private  (keeps your code secure)
  4. Do NOT tick "Add a README" or any other options
  5. Click "Create repository"

Then run these two commands:

  git remote add origin https://github.com/av72245/lendlyfin.git
  git push -u origin main

When prompted for a password, use a Personal Access Token (not your
GitHub password):
  -> https://github.com/settings/tokens/new
  -> Tick the "repo" scope -> Generate -> copy it -> paste as password

Your code is now live on GitHub. DONE.


=================================================================
 STEP 2 — DEPLOY FRONTEND ON NETLIFY  (free, ~5 min)
=================================================================

  1. Go to:  https://netlify.com -> Sign up or Log in
  2. Click "Add new site" -> "Import an existing project"
  3. Choose "Deploy with GitHub" -> authorise -> pick "lendlyfin"
  4. Settings to fill in:
       Base directory:    frontend
       Build command:     (leave blank)
       Publish directory: frontend
  5. Click "Deploy site"

Your frontend URL will be:  https://lendlyfin.netlify.app
(rename it in Site Settings -> Domain management)

Every git push auto-deploys the frontend. DONE.


=================================================================
 STEP 3 — FREE DATABASE ON NEON  (~5 min)
=================================================================

Neon = free PostgreSQL database, no credit card needed.

  1. Go to:  https://neon.tech -> Sign up (use GitHub login)
  2. Create a new project -> name it "lendlyfin"
  3. Choose a region close to Australia (e.g. AWS us-west-2)
  4. Once created, click "Connection string" tab
  5. Copy the string — looks like:
       postgresql://user:pass@ep-xxx.us-west-2.aws.neon.tech/neondb?sslmode=require

Save this string. You will paste it into Render in Step 4.


=================================================================
 STEP 4 — DEPLOY BACKEND ON RENDER  (free, ~10 min)
=================================================================

  1. Go to:  https://render.com -> Sign up with GitHub
  2. Click "New +" -> "Web Service"
  3. Connect repo: av72245/lendlyfin
  4. Fill in these settings:
       Name:             lendlyfin-api
       Root Directory:   backend
       Runtime:          Python 3
       Build Command:    pip install -r requirements.txt
       Start Command:    uvicorn app.main:app --host 0.0.0.0 --port $PORT
       Instance Type:    Free

  5. Scroll down to "Environment Variables" and add ALL of these:

     Key                          Value
     -------------------------------------------------------------------
     APP_ENV                      production
     SECRET_KEY                   (click "Generate" for a random value)
     ALGORITHM                    HS256
     ACCESS_TOKEN_EXPIRE_MINUTES  60
     DATABASE_URL                 (paste your Neon connection string)
     ADMIN_EMAIL                  admin@lendlyfin.com.au
     ADMIN_PASSWORD               (choose a strong password)
     BROKER_EMAIL                 broker@lendlyfin.com.au
     BROKER_PASSWORD              (choose a strong password)
     SENDGRID_API_KEY             (add in Step 6 — can skip for now)
     EMAIL_FROM                   hello@lendlyfin.com.au
     EMAIL_FROM_NAME              Lendlyfin
     BROKER_NOTIFICATION_EMAIL    your@email.com
     ALLOWED_ORIGINS              https://lendlyfin.netlify.app

  6. Click "Create Web Service"

Render builds and deploys. Your backend URL will be:
  https://lendlyfin-api.onrender.com

NOTE: Free tier sleeps after 15 min idle. First request wakes it
in ~30 seconds — totally normal for low traffic. DONE.


=================================================================
 STEP 5 — CONNECT FRONTEND TO BACKEND
=================================================================

  1. Open:  frontend/api.js
  2. Find this line near the top:
       const RENDER_BACKEND_URL = 'https://lendlyfin-api.onrender.com';
  3. If Render gave you a DIFFERENT URL, replace it here.
  4. Save, then push:
       git add frontend/api.js
       git commit -m "Update backend URL"
       git push

Netlify auto-deploys in ~30 seconds.

Also update ALLOWED_ORIGINS in Render dashboard:
  Render -> lendlyfin-api -> Environment
  Set ALLOWED_ORIGINS to your actual Netlify URL.

DONE.


=================================================================
 STEP 6 — EMAIL ALERTS (optional, highly recommended)
=================================================================

SendGrid emails you every time someone fills in a contact form.
Free tier = 100 emails/day.

  1. Go to:  https://sendgrid.com -> Sign up (free)
  2. Verify your email address (takes ~5 min)
  3. Settings -> API Keys -> Create API Key
  4. Name: "lendlyfin", permission: Full Access -> Create
  5. Copy the key (starts with SG.)
  6. Add to Render -> Environment Variables:
       SENDGRID_API_KEY = SG.your-key-here

DONE.


=================================================================
 STEP 7 — YOUR CALENDLY LINK
=================================================================

Replace the placeholder Calendly URL in these 4 files:
  frontend/contact.html
  frontend/refinancing.html
  frontend/referrals.html
  frontend/index.html

Find:     https://calendly.com/lendlyfin
Replace:  https://calendly.com/YOUR-REAL-CALENDLY-LINK

Then commit and push — Netlify auto-deploys.


=================================================================
 STEP 8 — CUSTOM DOMAIN (optional)
=================================================================

If you have lendlyfin.com.au:

  Netlify (frontend):
    Site settings -> Domain management -> Add custom domain
    Follow the DNS instructions shown

  Render (backend):
    Settings -> Custom domain -> e.g. api.lendlyfin.com.au

  Update ALLOWED_ORIGINS in Render to include your real domain.


=================================================================
 QUICK REFERENCE — YOUR LIVE URLS
=================================================================

  GitHub repo:  https://github.com/av72245/lendlyfin
  Frontend:     https://lendlyfin.netlify.app
  Backend API:  https://lendlyfin-api.onrender.com
  Admin panel:  https://lendlyfin.netlify.app/admin


=================================================================
 HOW TO UPDATE THE SITE AFTER GOING LIVE
=================================================================

Any change is 3 commands:

  git add .
  git commit -m "describe what you changed"
  git push

Netlify updates the frontend in ~30 seconds.
Render updates the backend in ~2 minutes.


=================================================================
 TROUBLESHOOTING
=================================================================

Contact forms not working?
  -> Check Render logs: dashboard -> lendlyfin-api -> Logs
  -> Confirm ALLOWED_ORIGINS includes your Netlify URL
  -> Confirm DATABASE_URL is correctly set to Neon

Backend slow on first load?
  -> Normal — free tier sleeps after 15 min idle, wakes in ~30s
  -> Upgrade to Render Starter ($7/mo) to keep it always awake

Database connection errors?
  -> In Neon dashboard, check your project isn't paused
  -> Free tier pauses after 5 days of inactivity — click "Resume"

Useful docs:
  Render:  https://render.com/docs
  Netlify: https://docs.netlify.com
  Neon:    https://neon.tech/docs

=================================================================
