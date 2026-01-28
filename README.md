# 📞 Exotel IVR Dashboard

A comprehensive, real-time analytics dashboard for monitoring and analyzing Exotel IVR systems. Built with Streamlit and Python, featuring call analytics, IVR tracking, cost analysis, and more.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## ✨ Features

- **📊 Real-time Analytics**: Live call metrics with date range filtering
- **📈 Interactive Charts**: Beautiful visualizations using Plotly
- **📋 Call Logs**: Searchable call history with export capability
- **🔥 Heatmap Analysis**: Identify peak call times and patterns
- **💰 Cost Tracking**: Monitor and analyze call costs
- **🔀 IVR Flow Analysis**: Complete IVR journey tracking with funnel charts
- **📄 Raw Data View**: API response viewer with testing capabilities
- **🎯 Webhook Support**: Capture IVR digit inputs in real-time (optional)

## 🚀 Quick Start

### Deploy to Streamlit Cloud (Recommended)

1. **Fork this repository**
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Deploy your app:**
   - Repository: `your-username/IVR_Dashboard`
   - Branch: `main`
   - Main file: `app.py`
4. **Add secrets** in Streamlit Cloud dashboard:
   ```toml
   # .streamlit/secrets.toml
   EXOTEL_API_KEY = "your_api_key_here"
   EXOTEL_API_TOKEN = "your_api_token_here"
   EXOTEL_SID = "your_account_sid_here"
   ```

### Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/IVR_Dashboard.git
   cd IVR_Dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Exotel credentials
   ```

4. **Run the dashboard:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser:**
   http://localhost:8501

## 🔑 Configuration

### Exotel API Credentials

Get your credentials from [Exotel Dashboard](https://my.exotel.com) → Settings → API Settings

**For Streamlit Cloud:** Add to Secrets Management  
**For Local:** Add to `.env` file

```env
EXOTEL_API_KEY=your_api_key_here
EXOTEL_API_TOKEN=your_api_token_here
EXOTEL_SID=your_account_sid_here
```

## 📊 Dashboard Sections

### 1. Key Metrics
- Total Calls
- Success Rate
- Average Duration
- Total Cost

### 2. Analytics Tab
- Call status distribution
- Duration patterns
- Call volume trends over time

### 3. Call Logs Tab
- Complete call history
- Advanced filtering (status, direction, phone number)
- CSV export

### 4. Heatmap Tab
- Hourly call patterns
- Day-wise distribution
- Peak time identification

### 5. Cost Analysis Tab
- Daily cost breakdown
- Cost per call metrics
- Total spending trends

### 6. IVR Flow Tab
- IVR path analysis
- Customer journey funnel
- Drop-off identification
- Language & service preferences

### 7. Raw Data Tab
- API response viewer
- Endpoint testing
- JSON data inspection

## 🎯 Features Explained

### Date Range Filtering
- Select custom date ranges in sidebar
- Automatically filters API calls
- Works with both live and sample data
- Up to 1000 records per request

### Live vs Sample Data
- **Sample Data Mode** (Default): Pre-generated data for testing
- **Live Data Mode**: Real-time data from Exotel API
- Toggle in sidebar

### IVR Tracking (Advanced)
For complete IVR digit capture, see [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)

## 📦 Dependencies

```
streamlit==1.29.0
pandas==2.1.4
plotly==5.18.0
requests==2.31.0
python-dotenv==1.0.0
flask==3.0.0
```

## 🛠️ Advanced Setup

### IVR Input Capture (Optional)

To track what buttons customers press in your IVR:

1. **Run webhook server:**
   ```bash
   python webhook_server.py
   ```

2. **Deploy webhook publicly:**
   - Use ngrok for testing
   - Deploy to cloud for production
   - See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)

3. **Configure Exotel Passthru applets:**
   - Add Passthru after each Gather step
   - Point to your webhook URLs
   - See [IVR_SETUP_GUIDE.md](IVR_SETUP_GUIDE.md)

## 📖 Documentation

- [QUICK_START.md](QUICK_START.md) - Quick reference guide
- [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) - Webhook deployment guide
- [IVR_SETUP_GUIDE.md](IVR_SETUP_GUIDE.md) - Exotel IVR configuration
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details

## 🔒 Security

- Never commit `.env` file to GitHub
- Use Streamlit Cloud Secrets for credentials
- Consider webhook authentication for production
- Use HTTPS for webhook endpoints

## 🚀 Deployment

### Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Connect repository in Streamlit Cloud
3. Add secrets in dashboard
4. Deploy!

### Heroku
```bash
echo "web: streamlit run app.py --server.port=\$PORT" > Procfile
git push heroku main
```

## 📝 License

This project is open source and available under the MIT License.

## 🙋 Support

- Check documentation files
- Exotel API: https://developer.exotel.com
- Open an issue on GitHub

---

Made with ❤️ for better IVR analytics
