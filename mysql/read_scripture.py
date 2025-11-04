import sqlite3

def get_verse_text(db_path, verse_title):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to get the scripture text for the given verse title
    cursor.execute("SELECT scripture_text FROM scriptures WHERE verse_title = ?", (verse_title,))
    result = cursor.fetchone()
    
    # Close the connection
    cursor.close()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None

if __name__ == "__main__":
    db_file = 'lds-scriptures-sqlite.db'  # Adjust path if needed
    verse = 'John 3:16'
    
    text = get_verse_text(db_file, verse)
    if text:
        print(f"{verse}: {text}")
    else:
        print(f"Verse '{verse}' not found in the database.")

