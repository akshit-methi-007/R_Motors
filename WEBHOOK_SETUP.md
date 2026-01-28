# Webhook Server Setup Guide

## Overview
The webhook server captures IVR digit inputs from Exotel Passthru applets in real-time and stores them in a local SQLite database. The dashboard can then merge this data with call records to provide complete IVR analytics.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Add to your `.env` file:
```bash
# Webhook Server Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
FLASK_DEBUG=True

# Database
IVR_DB_PATH=ivr_data.db

# Exotel API (already configured)
EXOTEL_API_KEY=your_api_key
EXOTEL_API_TOKEN=your_api_token
EXOTEL_SID=your_sid
```

### 3. Run the Webhook Server
```bash
python webhook_server.py
```

The server will start on `http://localhost:5000`

### 4. Test the Server
```bash
curl http://localhost:5000/webhook/test
```

Expected response:
```json
{
  "status": "active",
  "message": "Exotel IVR Webhook Server is running",
  "timestamp": "2026-01-23T..."
}
```

## Production Deployment

### Option 1: Using ngrok (for testing)
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start ngrok tunnel
ngrok http 5000

# Use the ngrok URL in Exotel Passthru applets
# Example: https://abc123.ngrok.io/webhook/ivr/language
```

### Option 2: Deploy to Cloud (Production)

#### A. Deploy to Heroku
```bash
# Create Procfile
echo "web: python webhook_server.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### B. Deploy to AWS EC2
```bash
# On your EC2 instance
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run with gunicorn (production server)
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webhook_server:app
```

#### C. Deploy to DigitalOcean App Platform
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically

## Configure Exotel Passthru Applets

### 1. Login to Exotel Dashboard
Go to https://my.exotel.com

### 2. Edit Your IVR Flow
Navigate to: Applets → Your IVR Flow → Edit

### 3. Add Passthru Applet After Each Gather

For each step in your IVR flow, add a Passthru applet:

**Language Step (after first Gather):**
- Applet: Passthru
- URL: `https://your-domain.com/webhook/ivr/language`
- Method: GET or POST
- Next Applet: Continue to State selection

**State Step:**
- URL: `https://your-domain.com/webhook/ivr/state`

**Service Step:**
- URL: `https://your-domain.com/webhook/ivr/service`

**Model Step:**
- URL: `https://your-domain.com/webhook/ivr/model`

**HP Step:**
- URL: `https://your-domain.com/webhook/ivr/hp`

### 4. Flow Diagram
```
[Incoming Call]
      ↓
[Play Welcome + Gather Language]
      ↓
[Passthru → /webhook/ivr/language]  ← Captures digit input
      ↓
[Play State + Gather State]
      ↓
[Passthru → /webhook/ivr/state]     ← Captures digit input
      ↓
[Play Service + Gather Service]
      ↓
[Passthru → /webhook/ivr/service]   ← Captures digit input
      ↓
[Continue...]
```

## Webhook Endpoints

### IVR Input Endpoints
- `POST /webhook/ivr/language` - Language selection (1=Hindi, 2=English)
- `POST /webhook/ivr/state` - State selection
- `POST /webhook/ivr/service` - Service type selection
- `POST /webhook/ivr/model` - Model/year selection
- `POST /webhook/ivr/hp` - HP/power selection

### API Endpoints (for integration)
- `GET /api/ivr/paths` - Get all IVR paths
  - Query params: `start_date`, `end_date`
  - Example: `/api/ivr/paths?start_date=2026-01-01&end_date=2026-01-31`

- `GET /api/ivr/stats` - Get IVR statistics
  - Returns: Total calls, top paths, language distribution

- `GET /webhook/test` - Health check endpoint

## Database Schema

### Table: ivr_inputs (Raw inputs)
```sql
CREATE TABLE ivr_inputs (
    id INTEGER PRIMARY KEY,
    call_sid TEXT NOT NULL,
    from_number TEXT,
    to_number TEXT,
    step_name TEXT NOT NULL,
    digit_input TEXT,
    timestamp DATETIME,
    exophone TEXT,
    caller_circle TEXT
);
```

### Table: ivr_paths (Aggregated paths)
```sql
CREATE TABLE ivr_paths (
    id INTEGER PRIMARY KEY,
    call_sid TEXT UNIQUE NOT NULL,
    from_number TEXT,
    to_number TEXT,
    language_choice TEXT,
    state_choice TEXT,
    service_choice TEXT,
    model_choice TEXT,
    hp_choice TEXT,
    complete_path TEXT,
    timestamp DATETIME
);
```

## Using IVR Data in Dashboard

### 1. Start Webhook Server
```bash
python webhook_server.py
```

### 2. Start Dashboard
```bash
streamlit run app.py
```

### 3. Enable Live Data
In the dashboard sidebar:
- ✅ Check "Use Live Exotel Data"
- The dashboard will automatically merge IVR data from the database

### 4. View IVR Analytics
Navigate to the "IVR Flow" tab to see:
- IVR completion rates
- Most popular paths
- Language preferences
- State-wise distribution
- Service selection patterns

## Monitoring & Maintenance

### View Database Contents
```bash
# Open SQLite database
sqlite3 ivr_data.db

# Query recent inputs
SELECT * FROM ivr_inputs ORDER BY timestamp DESC LIMIT 10;

# Query complete paths
SELECT * FROM ivr_paths ORDER BY timestamp DESC LIMIT 10;

# Get statistics
SELECT step_name, digit_input, COUNT(*) 
FROM ivr_inputs 
GROUP BY step_name, digit_input;
```

### Backup Database
```bash
# Backup
cp ivr_data.db ivr_data_backup_$(date +%Y%m%d).db

# Restore
cp ivr_data_backup_20260123.db ivr_data.db
```

### Logs
Check webhook server logs for debugging:
```bash
python webhook_server.py 2>&1 | tee webhook.log
```

## Troubleshooting

### Issue: Webhook not receiving data
**Solution:**
1. Check server is running: `curl http://localhost:5000/webhook/test`
2. Verify public URL is accessible (for ngrok/cloud deployment)
3. Check Exotel flow configuration - Passthru URLs must be correct
4. Check server logs for errors

### Issue: Database not found
**Solution:**
```bash
python ivr_database.py  # Initialize database
```

### Issue: IVR data not showing in dashboard
**Solution:**
1. Ensure webhook server is running
2. Make test calls to IVR system
3. Check database has data: `sqlite3 ivr_data.db "SELECT COUNT(*) FROM ivr_inputs;"`
4. Restart dashboard: Kill process and run `streamlit run app.py`

### Issue: Duplicate entries
**Solution:**
The system handles duplicates by using CallSid as unique key. If you see duplicates, check:
- Passthru applet isn't called multiple times in flow
- No circular flow references

## Security Considerations

### 1. Authentication
Add basic auth to webhook endpoints:
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'exotel' and password == 'your_secret_key'

@app.route('/webhook/ivr/<step_name>', methods=['GET', 'POST'])
@auth.login_required
def ivr_webhook(step_name):
    # ... existing code
```

### 2. IP Whitelisting
Only allow requests from Exotel IPs:
```python
ALLOWED_IPS = ['122.166.196.130', '122.166.196.131']  # Exotel IPs

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)
```

### 3. HTTPS
Always use HTTPS in production. Get free SSL with:
- Let's Encrypt (for custom domains)
- Cloudflare (free tier includes SSL)
- Heroku/AWS (SSL included)

## Advanced Features

### Export IVR Data
```python
# Export to CSV
import pandas as pd
from ivr_database import IVRDatabase

db = IVRDatabase()
df = db.get_ivr_paths()
df.to_csv('ivr_export.csv', index=False)
```

### Real-time Dashboard Updates
Add auto-refresh to dashboard:
```python
# In app.py sidebar
refresh_interval = st.slider("Auto-refresh (seconds)", 0, 300, 0)
if refresh_interval > 0:
    time.sleep(refresh_interval)
    st.rerun()
```

### Alerts & Notifications
Send alerts for specific patterns:
```python
# In webhook_server.py
def check_alerts(call_sid, complete_path):
    # Alert if customer drops at language selection
    if complete_path.startswith('-'):
        send_alert(f"Drop-off at language: {call_sid}")
```

## API Integration Examples

### Fetch IVR Paths Programmatically
```python
import requests

response = requests.get(
    'http://localhost:5000/api/ivr/paths',
    params={
        'start_date': '2026-01-01',
        'end_date': '2026-01-31'
    }
)

data = response.json()
print(f"Total paths: {data['count']}")
for path in data['data']:
    print(f"{path['call_sid']}: {path['complete_path']}")
```

### Get Statistics
```python
response = requests.get('http://localhost:5000/api/ivr/stats')
stats = response.json()

print(f"Total calls: {stats['total_calls']}")
print(f"Top paths: {stats['top_paths']}")
```

## Next Steps

1. ✅ Set up webhook server locally
2. ✅ Test with ngrok
3. ✅ Configure Passthru applets in Exotel
4. ✅ Make test calls to verify data capture
5. ✅ Deploy to production (cloud)
6. ✅ Monitor and analyze IVR patterns

## Support

For issues or questions:
- Check logs: `tail -f webhook.log`
- Review Exotel documentation: https://developer.exotel.com
- Test endpoints: `curl -X POST http://localhost:5000/webhook/test`
