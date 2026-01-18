import sqlite3
import xml.etree.ElementTree as ET
import os

# Define DB Name globally so it's consistent
DB_NAME = 'forensic.db'

def init_db():
    """Ensures the database table exists."""
    print("🛠️  Verifying Schema...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forensic_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        event_time TEXT,
        main_info TEXT,
        extra_details TEXT
    )
    """)
    conn.close()

def parse_xml_to_db(filepath):
    """
    Parses the XML file at 'filepath' and inserts data into the database.
    Returns: (True, "Success Message") or (False, "Error Message")
    """
    print(f"🔌 Connecting to {DB_NAME}...")
    
    # 1. Ensure DB exists
    init_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 2. Clear old data (Per your original logic)
    cursor.execute("DELETE FROM forensic_events")

    # 3. Parse XML
    print(f"📂 Parsing XML Report: {filepath}...")
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found!")
        return False, "File not found"
        
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        count = 0
        
        # SMS
        for sms in root.findall('.//message'):
            query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)"
            time = sms.find('timestamp').text.replace('T', ' ').replace('Z', '')
            cursor.execute(query, ('SMS', time, f"From: {sms.find('sender').text}", sms.find('body').text))
            count += 1

        # Calls
        for call in root.findall('.//call'):
            query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)"
            time = call.find('timestamp').text.replace('T', ' ').replace('Z', '')
            caller = call.find('caller').text if call.find('caller') is not None else "Unknown"
            info = f"{call.get('type')} Call: {caller}"
            cursor.execute(query, ('Call', time, info, f"Duration: {call.get('duration')}s"))
            count += 1

        # Web History
        for visit in root.findall('.//visit'):
            query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)"
            time = visit.find('timestamp').text.replace('T', ' ').replace('Z', '')
            cursor.execute(query, ('Web Visit', time, visit.find('title').text, visit.find('url').text))
            count += 1

        # --- GPS Locations (MOVED INSIDE TRY BLOCK) ---
        for loc in root.findall('.//location'):
            query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (?, ?, ?, ?)"
            time = loc.find('timestamp').text.replace('T', ' ').replace('Z', '')
            lat = loc.find('latitude').text
            lon = loc.find('longitude').text
            label = loc.find('label').text
            
            # We store the coordinates in 'main_info' so we can easily regex them later
            cursor.execute(query, ('GPS', time, f"Coords: {lat}, {lon}", label))
            count += 1

        conn.commit()
        print(f"✅ Success! {count} logs migrated to SQLite.")
        return True, f"Parsed {count} logs"

    except Exception as e:
        print(f"❌ Parsing Error: {e}")
        return False, str(e)
    finally:
        conn.close()

# --- BACKWARD COMPATIBILITY ---
if __name__ == "__main__":
    default_file = 'updated_mock_file.xml'
    parse_xml_to_db(default_file)
