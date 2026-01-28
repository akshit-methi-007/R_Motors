# IVR Data Capture Setup Guide

## Problem
The Exotel Calls API (`/v1/Accounts/{SID}/Calls.json`) **does NOT return IVR digit inputs**. 

You can see:
- ✅ Call duration, status, from/to numbers, price
- ❌ What buttons the user pressed in IVR (digit inputs)

## Solution: Use Passthru Applet

### What is Passthru?
Passthru is an Exotel applet that sends real-time call data to your webhook URL during the call flow.

### How to Capture IVR Inputs

#### 1. Setup Your Webhook Server

Create an endpoint to receive IVR data:

**Example with Flask (Python):**
```python
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/exotel/ivr-callback', methods=['GET'])
def ivr_callback():
    # Exotel sends data as query parameters
    call_sid = request.args.get('CallSid')
    digits = request.args.get('digits', '').strip('"')  # Remove quotes
    call_from = request.args.get('CallFrom')
    call_to = request.args.get('CallTo')
    call_status = request.args.get('CallStatus')
    
    # Store in database
    conn = sqlite3.connect('ivr_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ivr_inputs (call_sid, digits, call_from, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    ''', (call_sid, digits, call_from))
    conn.commit()
    conn.close()
    
    # Return 200 OK (or 302 for routing decision)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Example with FastAPI:**
```python
from fastapi import FastAPI, Query
from datetime import datetime

app = FastAPI()

@app.get("/exotel/ivr-callback")
async def ivr_callback(
    CallSid: str = Query(...),
    digits: str = Query(""),
    CallFrom: str = Query(""),
    CallTo: str = Query(""),
    CallStatus: str = Query("")
):
    # Remove quotes from digits
    digits_clean = digits.strip('"')
    
    # Store in your database
    save_to_database(CallSid, digits_clean, CallFrom)
    
    return {"status": "ok"}
```

#### 2. Configure Exotel Flow

1. Go to [Exotel Dashboard](https://my.exotel.com/apps)
2. Open your IVR Flow
3. Add **Passthru** applet after each **Gather** or **IVR Menu** applet:

```
[Greeting] → [IVR Menu/Gather] → [Passthru] → [Next Step]
                                      ↓
                                Your Webhook
```

#### 3. Configure Passthru Applet

- **URL**: `https://your-server.com/exotel/ivr-callback`
- **Mode**: Async (if you just want to store data) or Sync (if you want to route based on input)
- **Success/Failure Paths**: Configure what happens after Passthru

### Parameters Received in Passthru

When a user presses digits, Exotel will call your URL with these parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `CallSid` | Unique call ID | `CA12345678` |
| `digits` | Numbers pressed by user | `"1"`, `"12"`, `"123"` |
| `CallFrom` | Caller's number | `+919876543210` |
| `CallTo` | ExoPhone number | `+917200123456` |
| `CallStatus` | Current call status | `in-progress` |
| `Direction` | Call direction | `incoming` |
| `Created` | Call creation time | `2026-01-23 10:30:00` |

**Important:** The `digits` parameter comes with quotes (e.g., `"123"`). Strip them in your code.

### Sample Passthru URL

When someone presses `1-2-3` in your IVR, Exotel will call:

```
GET https://your-server.com/exotel/ivr-callback?CallSid=CA12345678&digits="123"&CallFrom=+919876543210&CallTo=+917200123456&CallStatus=in-progress&Direction=incoming&Created=2026-01-23%2010:30:00
```

### Database Schema Example

```sql
CREATE TABLE ivr_inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_sid VARCHAR(50) NOT NULL,
    digits VARCHAR(20),
    call_from VARCHAR(20),
    call_to VARCHAR(20),
    call_status VARCHAR(20),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_call_sid (call_sid)
);
```

### Linking IVR Data with Call Records

After setting up Passthru, you can join your IVR data with Exotel call data:

```python
# Fetch call data from Exotel API
calls_df = get_exotel_calls()

# Fetch IVR inputs from your database
ivr_df = get_ivr_inputs_from_database()

# Merge on CallSid
complete_data = calls_df.merge(ivr_df, on='CallSid', how='left')
```

## Your Current IVR Flow

Based on your flow:

```
Step 1: Language Selection (1=Hindi, 2=English)
Step 2: State Selection (1=Rajasthan, 2=MP, 3=Maharashtra, 4=Other)
Step 3: Service (1=Sell, 2=Buy Old, 3=Buy New, 4=Finance, 5=Other, 9=Consultant)
Step 4: Model Year (varies by service)
Step 5: HP Selection (for specific paths)
```

You should add Passthru applets after:
- ✅ Language selection (captures "1" or "2")
- ✅ State selection (captures "1", "2", "3", or "4")
- ✅ Service selection (captures "1", "2", "3", "4", "5", or "9")
- ✅ Model year selection (captures model year choice)
- ✅ HP selection (captures "1" or "2")

## Testing

1. Make a test call to your ExoPhone
2. Press digits in IVR
3. Check your webhook logs
4. Verify data is saved in database
5. Check Exotel logs if callback fails

## Troubleshooting

### Passthru not calling your URL?
- ✅ Check URL is publicly accessible
- ✅ Verify HTTPS certificate is valid
- ✅ Check Exotel flow is published (not draft)
- ✅ Ensure URL responds within 10 seconds

### Digits not captured?
- ✅ Passthru must be AFTER Gather/IVR applet
- ✅ Strip quotes from digits parameter
- ✅ Check Gather timeout settings

### Want to route calls based on digits?
- Use **Sync mode** in Passthru
- Return HTTP 200 for one path, 302 for another
- User will wait for your response (keep it fast!)

## Resources

- [Passthru Applet Documentation](https://support.exotel.com/support/solutions/articles/48283-working-with-passthru-applet)
- [Gather Applet Documentation](https://developer.exotel.com/applet/#gather)
- [IVR Menu Documentation](https://developer.exotel.com/applet/#ivr)
- [Exotel API Documentation](https://developer.exotel.com/api/)

## Next Steps

1. ✅ Set up a webhook server (Flask/FastAPI/Node.js)
2. ✅ Make it publicly accessible (ngrok for testing, proper domain for production)
3. ✅ Add Passthru applets in your Exotel flow
4. ✅ Test with a real call
5. ✅ Update this dashboard to fetch IVR data from your database
