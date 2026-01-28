"""
Exotel IVR Webhook Server
Receives and stores IVR digit inputs from Exotel Passthru applets
"""

from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
DB_PATH = os.getenv('IVR_DB_PATH', 'ivr_data.db')

def init_database():
    """Initialize SQLite database with IVR tracking table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ivr_inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT NOT NULL,
            from_number TEXT,
            to_number TEXT,
            step_name TEXT NOT NULL,
            digit_input TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            exophone TEXT,
            caller_circle TEXT,
            INDEX idx_call_sid (call_sid),
            INDEX idx_timestamp (timestamp)
        )
    """)
    
    # Create aggregated view for complete IVR paths
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ivr_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT UNIQUE NOT NULL,
            from_number TEXT,
            to_number TEXT,
            language_choice TEXT,
            state_choice TEXT,
            service_choice TEXT,
            model_choice TEXT,
            hp_choice TEXT,
            complete_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")

def store_ivr_input(call_sid, step_name, digit_input, from_number=None, 
                    to_number=None, exophone=None, caller_circle=None):
    """Store individual IVR input in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clean digit input (remove quotes if present)
    if digit_input:
        digit_input = digit_input.strip('"').strip("'")
    
    cursor.execute("""
        INSERT INTO ivr_inputs 
        (call_sid, from_number, to_number, step_name, digit_input, exophone, caller_circle)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (call_sid, from_number, to_number, step_name, digit_input, exophone, caller_circle))
    
    conn.commit()
    conn.close()

def update_ivr_path(call_sid, step_name, digit_input, from_number=None, to_number=None):
    """Update aggregated IVR path for a call"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clean digit input
    if digit_input:
        digit_input = digit_input.strip('"').strip("'")
    
    # Check if path exists
    cursor.execute("SELECT * FROM ivr_paths WHERE call_sid = ?", (call_sid,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing path
        if step_name == 'language':
            cursor.execute("""
                UPDATE ivr_paths 
                SET language_choice = ? 
                WHERE call_sid = ?
            """, (digit_input, call_sid))
        elif step_name == 'state':
            cursor.execute("""
                UPDATE ivr_paths 
                SET state_choice = ? 
                WHERE call_sid = ?
            """, (digit_input, call_sid))
        elif step_name == 'service':
            cursor.execute("""
                UPDATE ivr_paths 
                SET service_choice = ? 
                WHERE call_sid = ?
            """, (digit_input, call_sid))
        elif step_name == 'model':
            cursor.execute("""
                UPDATE ivr_paths 
                SET model_choice = ? 
                WHERE call_sid = ?
            """, (digit_input, call_sid))
        elif step_name == 'hp':
            cursor.execute("""
                UPDATE ivr_paths 
                SET hp_choice = ? 
                WHERE call_sid = ?
            """, (digit_input, call_sid))
    else:
        # Create new path
        cursor.execute("""
            INSERT INTO ivr_paths (call_sid, from_number, to_number, language_choice, state_choice, 
                                   service_choice, model_choice, hp_choice)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (call_sid, from_number, to_number, 
              digit_input if step_name == 'language' else None,
              digit_input if step_name == 'state' else None,
              digit_input if step_name == 'service' else None,
              digit_input if step_name == 'model' else None,
              digit_input if step_name == 'hp' else None))
    
    # Update complete path
    cursor.execute("""
        UPDATE ivr_paths 
        SET complete_path = COALESCE(language_choice, '') || '-' || 
                           COALESCE(state_choice, '') || '-' || 
                           COALESCE(service_choice, '') || '-' || 
                           COALESCE(model_choice, '') || '-' || 
                           COALESCE(hp_choice, '')
        WHERE call_sid = ?
    """, (call_sid,))
    
    conn.commit()
    conn.close()

@app.route('/webhook/ivr/<step_name>', methods=['GET', 'POST'])
def ivr_webhook(step_name):
    """
    Webhook endpoint for Exotel Passthru applets
    
    Configure in Exotel flow:
    - Language step: https://your-domain.com/webhook/ivr/language
    - State step: https://your-domain.com/webhook/ivr/state
    - Service step: https://your-domain.com/webhook/ivr/service
    - Model step: https://your-domain.com/webhook/ivr/model
    - HP step: https://your-domain.com/webhook/ivr/hp
    """
    try:
        # Get parameters from Exotel
        call_sid = request.args.get('CallSid') or request.form.get('CallSid')
        digit_input = request.args.get('digits') or request.form.get('digits')
        from_number = request.args.get('From') or request.form.get('From')
        to_number = request.args.get('To') or request.form.get('To')
        exophone = request.args.get('To') or request.form.get('To')
        caller_circle = request.args.get('CallerCircle') or request.form.get('CallerCircle')
        
        if not call_sid:
            return jsonify({'error': 'CallSid is required'}), 400
        
        # Store in database
        store_ivr_input(call_sid, step_name, digit_input, from_number, 
                       to_number, exophone, caller_circle)
        
        # Update aggregated path
        update_ivr_path(call_sid, step_name, digit_input, from_number, to_number)
        
        print(f"📞 IVR Input: CallSid={call_sid}, Step={step_name}, Digit={digit_input}")
        
        # Return response to Exotel (continue to next applet)
        return jsonify({
            'success': True,
            'message': f'IVR input recorded for {step_name}',
            'call_sid': call_sid,
            'digit': digit_input
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/test', methods=['GET'])
def test_webhook():
    """Test endpoint to verify webhook server is running"""
    return jsonify({
        'status': 'active',
        'message': 'Exotel IVR Webhook Server is running',
        'timestamp': datetime.now().isoformat(),
        'database': DB_PATH
    }), 200

@app.route('/api/ivr/paths', methods=['GET'])
def get_ivr_paths():
    """API endpoint to retrieve all IVR paths"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get optional date filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = "SELECT * FROM ivr_paths WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        paths = [dict(row) for row in rows]
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(paths),
            'data': paths
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ivr/stats', methods=['GET'])
def get_ivr_stats():
    """Get IVR statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total calls with IVR interaction
        cursor.execute("SELECT COUNT(DISTINCT call_sid) FROM ivr_inputs")
        total_calls = cursor.fetchone()[0]
        
        # Most common paths
        cursor.execute("""
            SELECT complete_path, COUNT(*) as count 
            FROM ivr_paths 
            WHERE complete_path IS NOT NULL 
            GROUP BY complete_path 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_paths = [{'path': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Language distribution
        cursor.execute("""
            SELECT language_choice, COUNT(*) as count 
            FROM ivr_paths 
            WHERE language_choice IS NOT NULL 
            GROUP BY language_choice
        """)
        language_dist = [{'language': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'total_calls': total_calls,
            'top_paths': top_paths,
            'language_distribution': language_dist
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get configuration from environment
    host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Exotel IVR Webhook Server                               ║
    ╠═══════════════════════════════════════════════════════════╣
    ║   Status: Running                                         ║
    ║   Host: {host}:{port}                                    ║
    ║   Database: {DB_PATH}                                     ║
    ║                                                           ║
    ║   Webhook Endpoints:                                      ║
    ║   • POST /webhook/ivr/language                            ║
    ║   • POST /webhook/ivr/state                               ║
    ║   • POST /webhook/ivr/service                             ║
    ║   • POST /webhook/ivr/model                               ║
    ║   • POST /webhook/ivr/hp                                  ║
    ║                                                           ║
    ║   API Endpoints:                                          ║
    ║   • GET /api/ivr/paths                                    ║
    ║   • GET /api/ivr/stats                                    ║
    ║   • GET /webhook/test                                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
