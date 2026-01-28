# 📞 Exotel IVR Dashboard - Quick Reference

## 🚀 Quick Start

### 1. Run Dashboard Only (Sample Data)
```bash
streamlit run app.py
```
Open browser to http://localhost:8501

### 2. Run with Live Exotel Data
```bash
# Configure .env first
streamlit run app.py
# Enable "Use Live Exotel Data" in sidebar
```

### 3. Run with IVR Tracking (Full System)
```bash
# Terminal 1: Webhook Server
python webhook_server.py

# Terminal 2: Dashboard
streamlit run app.py
```

## 📊 Available Reports

### From Exotel Calls API
✅ **Available Now:**
- Call logs with date filtering
- Call status (completed, busy, no-answer, failed)
- Duration and timestamps
- Caller/recipient numbers
- Direction (inbound/outbound)
- Cost/pricing
- Recording URLs

❌ **NOT Available from API:**
- IVR digit inputs (requires webhook setup)

### From Webhook Server (IVR Tracking)
✅ **Available with Setup:**
- Complete IVR paths
- Language choices
- State selections
- Service type selections
- Model/HP choices
- Drop-off points
- Path analytics

## 🔧 Feature Summary

| Feature | Status | Setup Required |
|---------|--------|----------------|
| Date Range Filtering | ✅ Ready | None - works out of box |
| Live API Data | ✅ Ready | Add credentials to .env |
| IVR Input Tracking | ✅ Ready | Run webhook_server.py + configure Exotel Passthru |
| Sample Data Mode | ✅ Ready | None |
| Export to CSV | ✅ Ready | None |
| Real-time Merging | ✅ Ready | Webhook server running |

## 📁 Project Files

```
IVR_Dashboard/
├── app.py                    # Main Streamlit dashboard
├── webhook_server.py         # Flask webhook server for IVR inputs
├── ivr_database.py          # Database operations for IVR data
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (create from .env.example)
├── README.md                # Full documentation
├── WEBHOOK_SETUP.md         # Webhook deployment guide
└── IVR_SETUP_GUIDE.md       # Exotel IVR configuration guide
```

## 🎯 What You Asked For

### 1. Reports API
**Answer:** Exotel doesn't have a separate "Reports API". Use:
- `/Calls.json` endpoint with date parameters (already implemented)
- Dashboard date range filtering (now available)
- Export to CSV from dashboard

### 2. Date Range Filtering
**Status:** ✅ Implemented
- Sidebar date picker sends dates to API
- Works with live Exotel data: `get_calls(start_date, end_date, limit=1000)`
- Also filters sample data

### 3. IVR Input Capture
**Status:** ✅ Complete System Implemented
- Webhook server ready to deploy
- Database schema created
- Dashboard integration complete
- Automatic merging of IVR + call data

## 🚀 Next Steps

1. **Test Date Filtering:**
   ```bash
   streamlit run app.py
   # Select date range in sidebar
   # Enable "Use Live Exotel Data"
   ```

2. **Deploy Webhook Server (for IVR tracking):**
   ```bash
   # Local testing with ngrok
   python webhook_server.py
   ngrok http 5000
   
   # Update Exotel flow with ngrok URL
   ```

3. **Configure Exotel Passthru Applets:**
   - See WEBHOOK_SETUP.md for step-by-step guide
   - Add Passthru after each Gather in your IVR flow
   - Point to webhook URLs

## 📞 Support

- **Exotel API Docs:** https://developer.exotel.com/api/
- **Webhook Setup:** See WEBHOOK_SETUP.md
- **IVR Configuration:** See IVR_SETUP_GUIDE.md
- **Database Schema:** See ivr_database.py

## 🔍 Testing

```bash
# Test dashboard
streamlit run app.py

# Test webhook server
curl http://localhost:5000/webhook/test

# Test IVR data capture
curl -X POST "http://localhost:5000/webhook/ivr/language?CallSid=test123&digits=1&From=9876543210"

# View database
sqlite3 ivr_data.db "SELECT * FROM ivr_inputs LIMIT 10;"
```

## ✅ Completed Features

1. ✅ Date range filtering in dashboard
2. ✅ API calls with date parameters
3. ✅ Webhook server for IVR inputs
4. ✅ SQLite database for IVR storage
5. ✅ Automatic data merging
6. ✅ Dashboard integration
7. ✅ Complete documentation
