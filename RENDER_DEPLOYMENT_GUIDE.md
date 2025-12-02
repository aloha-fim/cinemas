# Deploying Cinema Booking App to Render.com

A step-by-step guide to deploy the FastAPI cinema booking system to Render.com with a PostgreSQL database.

---

## 📋 Prerequisites

Before you begin, make sure you have:

1. A [Render.com](https://render.com) account (free tier available)
2. Your code pushed to a GitHub or GitLab repository
3. The following files in your project root:
   - `requirements.txt` (already exists)
   - `main.py` (already exists)

---

## 🗂️ Project Structure

```
cinema_booking/
├── main.py              # FastAPI application entry point
├── database.py          # Database connection configuration
├── models.py            # SQLAlchemy models
├── requirements.txt     # Python dependencies
├── static/              # CSS and static assets
├── templates/           # Jinja2 HTML templates
└── tests/               # Test files
```

---

## 📝 Step 1: Prepare Your Repository

### 1.1 Push Your Code to GitHub

If you haven't already, initialize a git repository and push to GitHub:

```bash
cd cinema_booking
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cinema-booking.git
git push -u origin main
```

### 1.2 Verify requirements.txt

Your `requirements.txt` should include all dependencies:

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
python-dotenv==1.0.0
jinja2==3.1.3
python-multipart==0.0.6
alembic==1.13.1
gunicorn==21.2.0
```

> **Note:** Add `gunicorn` if not present - Render uses it for production.

---

## 🗄️ Step 2: Create PostgreSQL Database on Render

### 2.1 Create New PostgreSQL Instance

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in the details:

| Field | Value |
|-------|-------|
| Name | `cinema-booking-db` |
| Database | `cinema_booking` |
| User | `cinema_user` |
| Region | Choose closest to your users |
| Plan | Free (or paid for production) |

4. Click **"Create Database"**

### 2.2 Get Database Connection String

After creation, go to your database dashboard and find the **Internal Database URL** under "Connections". It looks like:

```
postgresql://cinema_user:PASSWORD@dpg-xxxxx-a.oregon-postgres.render.com/cinema_booking
```

> **Important:** Use the **Internal URL** for services on Render (faster, free). Use **External URL** only for connecting from outside Render.

---

## 🚀 Step 3: Create Web Service on Render

### 3.1 Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub/GitLab repository
3. Select your `cinema-booking` repository

### 3.2 Configure Build Settings

| Setting | Value |
|---------|-------|
| **Name** | `cinema-booking` |
| **Region** | Same as your database |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (or paid) |

### 3.3 Add Environment Variables

Under **"Environment"**, add the following:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your PostgreSQL Internal URL from Step 2.2 |
| `PYTHON_VERSION` | `3.12.0` |

> **Render Note:** Render automatically provides the `PORT` environment variable.

### 3.4 Create Web Service

Click **"Create Web Service"**. Render will:
1. Clone your repository
2. Install dependencies
3. Start your application

---

## ⚙️ Step 4: Alternative Configuration with render.yaml

For Infrastructure as Code, create a `render.yaml` in your project root:

```yaml
# render.yaml
databases:
  - name: cinema-booking-db
    databaseName: cinema_booking
    user: cinema_user
    plan: free
    region: oregon

services:
  - type: web
    name: cinema-booking
    runtime: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: cinema-booking-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.12.0
    autoDeploy: true
```

Then in Render Dashboard:
1. Go to **"Blueprints"** → **"New Blueprint Instance"**
2. Connect your repository
3. Render will automatically create all resources

---

## 🔧 Step 5: Production Considerations

### 5.1 Use Gunicorn for Production

For better performance, update your start command to use Gunicorn with Uvicorn workers:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

### 5.2 Health Check Endpoint

Add a health check endpoint to `main.py`:

```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

Then in Render settings, set:
- **Health Check Path:** `/health`

### 5.3 Static Files

Render serves static files automatically. Your existing setup works:

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

---

## 🔍 Step 6: Verify Deployment

### 6.1 Check Logs

In your Render dashboard:
1. Go to your web service
2. Click **"Logs"** tab
3. Look for: `Uvicorn running on http://0.0.0.0:PORT`

### 6.2 Test Your Application

Your app will be available at:
```
https://cinema-booking.onrender.com
```

Test these endpoints:
- `GET /` - Main menu
- `GET /health` - Health check (if added)
- `GET /setup` - Movie setup page

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Build fails** | Check `requirements.txt` for typos |
| **Database connection error** | Verify `DATABASE_URL` is set correctly |
| **App crashes on startup** | Check logs for Python errors |
| **Static files not loading** | Ensure `static/` folder is committed |
| **Templates not found** | Ensure `templates/` folder is committed |

### Database Connection Issues

If you see connection errors, verify:

1. **URL format** - Render PostgreSQL URLs start with `postgresql://`
2. **Internal vs External** - Use Internal URL for Render services
3. **SSL** - Render databases require SSL by default

Update `database.py` if needed:

```python
# For Render PostgreSQL with SSL
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Helps with connection drops
    )
```

### Cold Starts (Free Tier)

Free tier services spin down after 15 minutes of inactivity. First request after sleep takes ~30 seconds. Solutions:

1. Use a paid plan ($7/month)
2. Set up an external ping service (UptimeRobot, etc.)
3. Accept the cold start delay

---

## 📊 Monitoring

### Render Dashboard

Monitor your app in the Render dashboard:
- **Metrics:** CPU, Memory, Request count
- **Logs:** Real-time application logs
- **Events:** Deploy history, scaling events

### Application Logging

Add structured logging to your app:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup_event():
    logger.info("Starting Cinema Booking System...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
```

---

## 🔄 Continuous Deployment

Render automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys!
```

To disable auto-deploy:
1. Go to Settings → Build & Deploy
2. Toggle off "Auto-Deploy"

---

## 💰 Pricing Summary

| Resource | Free Tier | Paid |
|----------|-----------|------|
| **Web Service** | 750 hours/month, sleeps after 15min | $7+/month, always on |
| **PostgreSQL** | 256MB, 90 days retention | $7+/month, persistent |

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub/GitLab
- [ ] `requirements.txt` includes all dependencies
- [ ] PostgreSQL database created on Render
- [ ] Web service created and connected to repo
- [ ] `DATABASE_URL` environment variable set
- [ ] Build completes successfully
- [ ] App accessible at Render URL
- [ ] Database tables created (check via `/setup`)

---

## 🎉 You're Live!

Your Cinema Booking System is now deployed at:

```
https://YOUR-SERVICE-NAME.onrender.com
```

Share the link and start booking movie tickets! 🎬🍿
