import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import ollama
import google.generativeai as genai
# --- IMPORT YOUR MODULE ---
# This assumes you have the 'migrate_data.py' file in the same folder
from migrate_data import parse_xml_to_db, init_db

app = Flask(__name__)
CORS(app)
app.secret_key = 'super_secret_hackathon_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- HYBRID AI ARCHITECTURE ---
# Configure Google GenAI for cloud-based powerful analysis
try:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    genai_model = genai.GenerativeModel('gemini-pro')
    GENAI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Google GenAI unavailable: {e}. Falling back to local Gemma 2B.")
    GENAI_AVAILABLE = False

# --- GLOBAL MEMORY FOR CHAT ---
# This list stores the conversation history so Gemma remembers context
chat_history = []

# Ensure DB is ready on start
init_db()

def get_db_connection():
    conn = sqlite3.connect('forensic.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- HYBRID AI ROUTING LOGIC ---
def analyze_with_hybrid_ai(content, analysis_type="standard"):
    """
    Routes analysis to appropriate AI model:
    - Local Gemma 2B: Quick entity extraction, sensitive data (offline-capable)
    - Google GenAI: Complex analysis, summarization, pattern matching
    """
    if analysis_type == "complex" and GENAI_AVAILABLE:
        # Cloud-based powerful analysis for complex cases
        try:
            prompt = f"""
            You are a forensic AI expert. Analyze these logs for:
            1. Criminal activity patterns
            2. Timeline inconsistencies
            3. Key persons of interest
            4. Financial transactions or drug references
            5. Threat assessment
            
            LOGS:
            {content[:10000]}
            
            Provide a comprehensive forensic analysis with triage score.
            """
            response = genai_model.generate_content(prompt)
            return response.text, "Google GenAI"
        except Exception as e:
            print(f"❌ GenAI Error: {e}. Falling back to Gemma 2B.")
            return None, None
    else:
        # Local privacy-preserving analysis with Gemma 2B
        try:
            prompt = f"""
            You are a forensic expert using Google Gemma 2B.
            Extract entities and analyze these logs for suspicious activity.
            
            LOGS:
            {content[:6000]}
            
            Provide 3 crisp bullet points summarising the threats.
            """
            response = ollama.chat(model='gemma:2b', messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content'], "Gemma 2B"
        except Exception as e:
            print(f"❌ Gemma Error: {e}")
            return None, None

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

# --- HYBRID AI ANALYSIS ENDPOINT ---
@app.route('/analyze', methods=['POST'])
def analyze():
    global chat_history
    print("\n--- 🤖 Hybrid AI Analysis Requested ---")
    
    data = request.json
    content = data.get('content', 'No logs provided.')
    analysis_type = data.get('type', 'standard')  # 'standard' or 'complex'
    
    # 1. Reset History for New Analysis
    chat_history = []
    
    # 2. Perform Hybrid AI Analysis
    print(f"💻 Running {analysis_type} analysis...")
    result, ai_model = analyze_with_hybrid_ai(content, analysis_type)
    
    if result:
        # 3. Save Context to Memory
        chat_history.append({'role': 'user', 'content': content})
        chat_history.append({'role': 'assistant', 'content': result})
        
        print(f"✅ Analysis Complete via {ai_model}!")
        return jsonify({
            "summary": result,
            "model_used": ai_model,
            "analysis_type": analysis_type
        })
    else:
        return jsonify({
            "summary": "⚠️ Both AI models offline. Please check Ollama and Google API key."
        }), 503

# --- COMPLEX FORENSIC ANALYSIS (Cloud-powered) ---
@app.route('/analyze_complex', methods=['POST'])
def analyze_complex():
    """
    Uses Google GenAI for deep forensic analysis
    (Requires Google API key and internet connection)
    """
    if not GENAI_AVAILABLE:
        return jsonify({"error": "Google GenAI not available. Check API key."}), 503
    
    data = request.json
    content = data.get('content')
    
    result, model = analyze_with_hybrid_ai(content, "complex")
    if result:
        return jsonify({"analysis": result, "model": model})
    else:
        return jsonify({"error": "Complex analysis failed"}), 500

# --- CHAT ROUTE (Conversational Evidence Analysis) ---
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

# --- SYSTEM STATUS ---
@app.route('/api/status', methods=['GET'])
def system_status():
    return jsonify({
        "gemma_available": True,  # Local model always available
        "genai_available": GENAI_AVAILABLE,
        "architecture": "Hybrid (Local Gemma 2B + Cloud Google GenAI)"
    })

if __name__ == '__main__':
    print("""\n    --- FORENX HYBRID AI SERVER ---
    🔵 Local Mode: Gemma 2B (Ollama) - ACTIVE
    🟢 Cloud Mode: Google GenAI - {} 
    🏗️ Architecture: Hybrid (Local + Cloud)
    """.format("ACTIVE" if GENAI_AVAILABLE else "INACTIVE"))
    app.run(port=5001, debug=True)
