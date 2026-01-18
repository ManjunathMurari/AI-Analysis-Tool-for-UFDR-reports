import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import ollama

# --- IMPORT YOUR MODULE ---
# This assumes you have the 'migrate_data.py' file in the same folder
from migrate_data import parse_xml_to_db, init_db

app = Flask(__name__)
CORS(app)
app.secret_key = 'super_secret_hackathon_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- GLOBAL MEMORY FOR CHAT ---
# This list stores the conversation history so Gemma remembers context
chat_history = [] 

# Ensure DB is ready on start
init_db()

def get_db_connection():
    conn = sqlite3.connect('forensic.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/upload_page')
def upload_page():
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
        
        # Call the parser from your migrate_data.py file
        success, message = parse_xml_to_db(filepath)
        
        if success:
            return redirect(url_for('dashboard'))
        else:
            return f"Error processing file: {message}", 500

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM forensic_events ORDER BY event_time DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', events=events)

# --- LOCAL AI ANALYSIS ---
@app.route('/analyze', methods=['POST'])
def analyze():
    global chat_history
    print("\n--- 🤖 Local AI Analysis Requested ---")
    
    data = request.json
    content = data.get('content', 'No logs provided.')
    
    # 1. Reset History for New Analysis
    chat_history = [] 
    
    # 2. Create the Prompt
    prompt = f"""
    You are a forensic expert using Google Gemma 2B.
    Analyze these logs for suspicious activity (drugs, money, meetings).
    
    LOGS:
    {content[:6000]}
    
    Provide 3 crisp bullet points summarising the threats.
    """

    try:
        print("💻 Running Gemma 2B...")
        response = ollama.chat(model='gemma:2b', messages=[{'role': 'user', 'content': prompt}])
        summary = response['message']['content']
        
        # 3. Save Context to Memory
        chat_history.append({'role': 'user', 'content': prompt})
        chat_history.append({'role': 'assistant', 'content': summary})
        
        print("✅ Analysis Complete!")
        return jsonify({"summary": summary})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"summary": "⚠️ AI Offline. Is Ollama running?"})

# --- CHAT ROUTE (The New Feature) ---
@app.route('/chat_evidence', methods=['POST'])
def chat_evidence():
    global chat_history
    query = request.json.get('query')
    
    if not chat_history:
        return jsonify({"answer": "Please run the analysis first to load evidence."})

    try:
        # 1. Add User Question to History
        chat_history.append({'role': 'user', 'content': query})
        
        # 2. Ask Gemma (Sending the whole history)
        response = ollama.chat(model='gemma:2b', messages=chat_history)
        answer = response['message']['content']
        
        # 3. Add AI Answer to History
        chat_history.append({'role': 'assistant', 'content': answer})
        
        return jsonify({"answer": answer})
        
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == '__main__':
    print("--- FORENX SERVER (OFFLINE MODE) ACTIVE ---")
    app.run(port=5001, debug=True)
