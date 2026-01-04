import mysql.connector
import xml.etree.ElementTree as ET

def migrate():
    cnx = mysql.connector.connect(user='root', password='Manju@123', host='127.0.0.1', database='forensic_db')
    cursor = cnx.cursor()
    tree = ET.parse('updated_mock_file.xml')
    root = tree.getroot()

    # Clear old data to avoid duplicates
    cursor.execute("TRUNCATE TABLE forensic_events")

    # 1. Insert SMS
    for sms in root.findall('.//message'):
        query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (%s, %s, %s, %s)"
        time = sms.find('timestamp').text.replace('T', ' ').replace('Z', '')
        cursor.execute(query, ('SMS', time, f"From: {sms.find('sender').text}", sms.find('body').text))

    # 2. Insert Calls
    for call in root.findall('.//call'):
        query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (%s, %s, %s, %s)"
        time = call.find('timestamp').text.replace('T', ' ').replace('Z', '')
        info = f"{call.get('type')} Call: {call.find('caller').text}"
        cursor.execute(query, ('Call', time, info, f"Duration: {call.get('duration')}s"))

    # 3. Insert Web History
    for visit in root.findall('.//visit'):
        query = "INSERT INTO forensic_events (event_type, event_time, main_info, extra_details) VALUES (%s, %s, %s, %s)"
        time = visit.find('timestamp').text.replace('T', ' ').replace('Z', '')
        cursor.execute(query, ('Web Visit', time, visit.find('title').text, visit.find('url').text))

    cnx.commit()
    print("Database fully populated with all forensic categories!")
    cnx.close()

if __name__ == "__main__":
    migrate()