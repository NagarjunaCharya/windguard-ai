# WindGuard AI - Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

### Prerequisites
- Vercel account (https://vercel.com)
- Vercel CLI installed: `npm install -g vercel`
- GitHub authentication (already done)

### Method 1: Deploy via Vercel CLI (Recommended)

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Deploy from project root:**
   ```bash
   cd C:\Users\Nagarjuna\OneDrive\Desktop\CYPHER_3.02
   vercel
   ```

3. **Follow the prompts:**
   - Setup and deploy? **Yes**
   - Which scope? Choose your account
   - Link to existing project? **No**
   - Project name? **windguard-ai** (or press Enter)
   - Directory? **./** (current directory)
   - Override settings? **No**

4. **Production deployment:**
   ```bash
   vercel --prod
   ```

### Method 2: Deploy via GitHub Integration

1. **Push to GitHub** (already done):
   ```bash
   git push origin phase2-model
   ```

2. **Connect to Vercel:**
   - Go to https://vercel.com/dashboard
   - Click "New Project"
   - Import your GitHub repository: `NagarjunaCharya/windguard-ai`
   - Select branch: `phase2-model`
   - Framework Preset: **Other**
   - Click **Deploy**

### 🔧 Configuration

The project includes:
- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Lightweight serverless API (no PyTorch)
- ✅ `api/requirements.txt` - Minimal Python dependencies
- ✅ `.vercelignore` - Files to exclude from deployment

### 📁 Project Structure for Vercel

```
CYPHER_3.02/
├── vercel.json                          # Vercel config
├── .vercelignore                        # Exclude large files
├── api/
│   ├── index.py                         # Serverless API endpoint
│   └── requirements.txt                 # API dependencies
└── windguard-frontend/
    └── production/
        ├── windguard-dashboard.html     # Main dashboard
        ├── ar-guide.html                # AR maintenance guide
        ├── styles/
        └── images/
```

### 🌐 After Deployment

Your app will be available at:
- **Production URL:** `https://windguard-ai-xxxxx.vercel.app`
- **API Endpoint:** `https://windguard-ai-xxxxx.vercel.app/api`
- **Dashboard:** `https://windguard-ai-xxxxx.vercel.app/windguard-dashboard.html`

### ⚙️ Environment Variables (Optional)

If needed, add in Vercel dashboard under Settings > Environment Variables:
- `PYTHON_VERSION`: `3.11`

### 📝 Notes

1. **PyTorch Model:** The full BiLSTM model is NOT deployed due to size limits (50MB Vercel limit). The API uses mock predictions for demo purposes.

2. **For Production ML:** Consider:
   - Deploy backend separately on Railway, Render, or AWS Lambda
   - Use Vercel only for frontend static hosting
   - Connect frontend to external ML API

3. **Custom Domain:** You can add a custom domain in Vercel project settings.

### 🔥 Troubleshooting

**Build fails?**
- Check `vercel` logs in terminal
- Ensure Python version is 3.11
- Check that `api/requirements.txt` doesn't include torch

**API not working?**
- Verify routes in `vercel.json`
- Check function logs in Vercel dashboard
- Test API: `https://your-app.vercel.app/api/turbines`

**Frontend shows 404?**
- Check frontend path in routes
- Ensure files are in `windguard-frontend/production/`

### 🎯 Production Checklist

- [ ] Deploy to Vercel
- [ ] Test all pages (dashboard, AR guide)
- [ ] Test API endpoints (/api/turbines, /api/predict/1)
- [ ] Add custom domain (optional)
- [ ] Set up analytics (optional)
- [ ] Configure CORS if needed

---

## Alternative: Full Backend Deployment

For the **full ML model with PyTorch**, deploy backend separately:

### Option A: Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option B: Render.com
1. Go to https://render.com
2. New > Web Service
3. Connect GitHub repo
4. Build command: `pip install -r windguard-backend/requirements.txt`
5. Start command: `python windguard-backend/app.py`

Then update frontend API URL to point to Railway/Render backend.

---

**Need help? Check Vercel docs:** https://vercel.com/docs
