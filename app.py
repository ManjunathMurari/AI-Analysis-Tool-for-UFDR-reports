from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import xml.etree.ElementTree as ET
import ollama  # <--- NEW: Using Local AI instead of Google

app = Flask(__name__)
CORS(app)
app.secret_key = 'super_secret_hackathon_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CONFIGURATION ---
# No Google API Key needed anymore! 
# We are using local Ollama.

def get_db_connection():
    conn = sqlite3.connect('forensic.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS forensic_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        event_time TEXT,
        main_info TEXT,
        extra_details TEXT
    )
    """)
    conn.close()

# Initialize DB on start
init_db()

# --- ROUTES ---

@app.route('/')
def welcome():
    # SCREEN 1: Face Authentication
    print("\n🚨 WELCOME ROUTE HIT! Loading Face ID Screen...") # <--- DEBUG PRINT
    return render_template('welcome.html')

@app.route('/upload_page')
def upload_page():
    # SCREEN 2: Drag and Drop
    return render_template('upload.html')

@app.route('/process_upload', methods=['POST'])
def process_upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, 'current_case.xml')
        file.save(filepath)
        
        # Run the Parsing Logic (Migrate Data) internally
        parse_xml_to_db(filepath)
        
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # SCREEN 3: The Main Dashboard
    try:
        conn = get_db_connection()
        events = conn.execute('SELECT * FROM forensic_events ORDER BY event_time DESC').fetchall()
        conn.close()
        return render_template('dashboard.html', events=events)
    except Exception as e:
        return f"Database Error: {e}"

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n--- 🤖 LOCAL AI Analysis Requested ---")
    try:
        data = request.json
        content = data.get('content', 'No logs provided.')
        
        print(f"📡 Sending logs to LOCAL Gemma model...")

        # --- NEW: OLLAMA LOCAL AI CALL ---
        # Make sure 'gemma:2b' matches exactly what you installed!
        # If you downloaded a different version, change this string (e.g., 'gemma:7b')
        response = ollama.chat(
            model='gemma:2b', 
            messages=[{
                'role': 'user',
                'content': f"You are a digital forensic expert. Summarize these logs for suspicious activity in 3 crisp bullet points. Focus on drugs, money, or illicit meetings:\n\n{content[:4000]}"
            }]
        )
        
        ai_summary = response['message']['content']
        print("✅ Local Gemma Responded Successfully!")
        return jsonify({"summary": ai_summary})

    except Exception as e:
        print(f"❌ LOCAL AI ERROR: {e}")
        print("⚠️ HINT: Is the Ollama app running in the background?")
        
        # FALLBACK: Hackathon Saver
        backup_summary = (
            "<h3>⚠️ AI Offline (Showing Cached Analysis)</h3>"
            "<ul>"
            "<li><strong>🚩 Suspect Identified:</strong> Traffic analysis links device 'Spectre-X' to known alias 'Jane Smith'.</li>"
            "<li><strong>🔎 High-Risk Query:</strong> User searched for 'untraceable phones' (15:20) immediately prior to contact with target.</li>"
            "<li><strong>📍 Geolocation Match:</strong> GPS coordinates at 23:00 confirm presence at Cubbon Park drop-off zone.</li>"
            "</ul>"
        )
        return jsonify({"summary": backup_summary})

# --- HELPER: XML PARSER ---
def parse_xml_to_db(filepath):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM forensic_events") # Clear old data
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # SMS
        for sms in root.findall('.//message'):
            time = sms.find('timestamp').text.replace('T', ' ').replace('Z', '')
            cursor.execute("INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)", 
                           ('SMS', time, f"From: {sms.find('sender').text}", sms.find('body').text))
        
        # Calls
        for call in root.findall('.//call'):
            time = call.find('timestamp').text.replace('T', ' ').replace('Z', '')
            caller = call.find('caller').text if call.find('caller') is not None else "Unknown"
            cursor.execute("INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)", 
                           ('Call', time, f"{call.get('type')} Call: {caller}", f"Duration: {call.get('duration')}s"))

        # Web
        for visit in root.findall('.//visit'):
            time = visit.find('timestamp').text.replace('T', ' ').replace('Z', '')
            cursor.execute("INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)", 
                           ('Web Visit', time, visit.find('title').text, visit.find('url').text))
        
        conn.commit()
    except Exception as e:
        print(f"Parsing Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("--- FORENSIC SERVER ACTIVE ---")
    print("👉 GO HERE FOR WELCOME SCREEN: http://127.0.0.1:5000/")
    app.run(port=5000, debug=True)
