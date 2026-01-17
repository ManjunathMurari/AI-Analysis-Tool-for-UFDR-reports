import sqlite3
import xml.etree.ElementTree as ET
import os

def migrate():
    print("🔌 Connecting to SQLite Database...")
    # This creates the file 'forensic.db' automatically if it doesn't exist
    conn = sqlite3.connect('forensic.db')
    cursor = conn.cursor()

    # 1. Create Table (SQLite syntax)
    print("🛠️  Verifying Schema...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forensic_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        event_time TEXT,
        main_info TEXT,
        extra_details TEXT
    )
    """)

    # 2. Clear old data
    cursor.execute("DELETE FROM forensic_events")

    # 3. Parse XML
    print("📂 Parsing XML Report...")
    if not os.path.exists('updated_mock_file.xml'):
        print("❌ Error: 'updated_mock_file.xml' not found!")
        return
        
    tree = ET.parse('updated_mock_file.xml')
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

    conn.commit()
    print(f"✅ Success! {count} logs migrated to SQLite.")
    conn.close()

if __name__ == "__main__":
    migrate()
