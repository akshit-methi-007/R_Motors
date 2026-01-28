# 🚀 Streamlit Cloud Deployment Guide

## Step-by-Step Instructions

### 1. Push to GitHub

```bash
cd /path/to/IVR_Dashboard_Deploy

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - Exotel IVR Dashboard"

# Add remote (create repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/IVR_Dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in with GitHub**

3. **Click "New app"**

4. **Configure deployment:**
   - Repository: `YOUR_USERNAME/IVR_Dashboard`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: Choose your custom URL (e.g., `my-ivr-dashboard`)

5. **Click "Deploy"**

### 3. Add Secrets

In Streamlit Cloud dashboard:

1. Go to your app settings (⚙️ icon)
2. Click "Secrets"
3. Add your Exotel credentials:

```toml
# .streamlit/secrets.toml format

EXOTEL_API_KEY = "c3f5799302e41bb1ebab44fbf660e238f8fa43921a110f72"
EXOTEL_API_TOKEN = "e84abd5585d9ca95574108425daaf50a2daa17e83aac256d"
EXOTEL_SID = "the691"
```

4. Click "Save"

### 4. Wait for Deployment

- Streamlit Cloud will install dependencies
- Build process takes 2-5 minutes
- Your app will be live at: `https://your-app-name.streamlit.app`

## 🔧 Configuration for Streamlit Cloud

The app automatically detects Streamlit Cloud and uses `st.secrets` instead of `.env` file.

No code changes needed! The app checks:
```python
# In app.py, it already handles both:
EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY', '')  # Local
# OR
EXOTEL_API_KEY = st.secrets.get('EXOTEL_API_KEY', '')  # Streamlit Cloud
```

## ✅ Checklist

Before deploying:

- [ ] Code pushed to GitHub
- [ ] `.env` file is NOT in repository (check `.gitignore`)
- [ ] `.env.example` is in repository (for reference)
- [ ] `requirements.txt` is present
- [ ] `.streamlit/config.toml` is configured
- [ ] README.md is updated with your app URL

After deploying:

- [ ] Secrets added in Streamlit Cloud
- [ ] App loads without errors
- [ ] Can toggle "Use Live Exotel Data"
- [ ] Live data fetches successfully
- [ ] All tabs work properly

## 🐛 Troubleshooting

### Issue: App not loading

**Solution:** Check logs in Streamlit Cloud dashboard for errors

### Issue: "No module named 'dotenv'"

**Solution:** Ensure `requirements.txt` has `python-dotenv==1.0.0`

### Issue: API credentials not working

**Solution:** 
1. Verify secrets are added correctly (no extra quotes)
2. Check secret names match exactly: `EXOTEL_API_KEY`, `EXOTEL_API_TOKEN`, `EXOTEL_SID`
3. Reboot app after adding secrets

### Issue: Database errors

**Solution:** Database features work locally only. For Streamlit Cloud, use sample data or configure external database.

## 🔄 Updating Your App

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud auto-deploys on push!
```

## 📊 App URL

After deployment, share your dashboard:

**Your App:** `https://YOUR-APP-NAME.streamlit.app`

Update README.md badge with your actual URL:
```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-NAME.streamlit.app)
```

## 🎉 You're Live!

Your Exotel IVR Dashboard is now accessible from anywhere!

- ✅ No server management needed
- ✅ Auto-deploys on git push
- ✅ Free SSL certificate
- ✅ Custom domain support (paid plan)

## 🔐 Security Notes

- Secrets are encrypted in Streamlit Cloud
- Never expose API credentials in code
- Use environment variables / secrets only
- `.gitignore` prevents `.env` from being committed

## 📱 Sharing

Share your dashboard with:
- Team members
- Clients
- Stakeholders

Just send them the URL!

## 🚀 Next Steps

1. Test your live dashboard
2. Share with your team
3. Monitor call analytics
4. Optionally: Set up webhook server for IVR tracking (see WEBHOOK_SETUP.md)

---

**Need Help?** Check Streamlit docs: https://docs.streamlit.io/streamlit-community-cloud
