import sqlite3
import glob
import random
import os
import re

# Use file-relative paths so the script can be run from the repository root
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'scriptures.db')


def search_verses_by_word(word):
    """Search all verses for a word (is case-insensitive) and print all matches, highlighting the word in pink. Loosen whole-word match to allow punctuation. Display Book name, chapter, and verse number before each verse, with tabs before and after. Also print debug info on match counts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT v.text, c.chapter_num, b.book_name, v.verseno FROM verse v JOIN chapter c ON v.chapter_id = c.id JOIN book b ON c.book_id = b.id WHERE LOWER(v.text) LIKE ?", (f"%{word.lower()}%",))
        results = cursor.fetchall()
        print(f"[DEBUG] SQL returned {len(results)} verses containing '{word}' as substring.")  # Debug output
        if results:
            # Loosened regex: match word boundaries or punctuation
            word_re = re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", re.IGNORECASE)
            filtered = []
            for text, chapter_num, book_name, verseno in results:
                if word_re.search(text):
                    filtered.append((text, chapter_num, book_name, verseno))
            print(f"[DEBUG] Regex loose filter matched {len(filtered)} verses.")  # Debug output
            if filtered:
                print(f"\nVerses containing '{word}':")
                for text, chapter_num, book_name, verseno in filtered:
                    if book_name.startswith("Volume "):
                        vol_num = book_name.split(" ")[-1]
                        display_name = f"Articles of Faith Vol. {vol_num}"
                    else:
                        display_name = book_name
                    def highlight(match):
                        return f"\033[95m{match.group(0)}\033[0m"
                    highlighted_text = word_re.sub(highlight, text)
                    print(f"\n\t{display_name} {chapter_num}:{verseno}\n\t{highlighted_text}\n")
        else:
            print(f"There are verses found containing the word: '{word}'.")
    except Exception as e:
        print(f"Error searching verses: {e}")
    finally:
        conn.close()
def build_database():
    """Run all .sql files located next to this script to build the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sql_files = glob.glob(os.path.join(BASE_DIR, "*.sql"))
    for sql_file in sql_files:
        print(f"Running {os.path.basename(sql_file)}...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            try:
                cursor.executescript(sql_script)
                print(f"Executed {os.path.basename(sql_file)} successfully.")
            except Exception as e:
                print(f"Error executing {os.path.basename(sql_file)}: {e}")
    conn.commit()
    conn.close()
    print("Database setup is complete.")

def get_specific_verse(book_name, chapter, verse_num):
    """Return the text of a specific verse given book name, chapter, and verse number."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Find the book_id for the given book_name (is case-insensitive)
        cursor.execute("SELECT id FROM book WHERE LOWER(book_name) = LOWER(?)", (book_name,))
        result = cursor.fetchone()
        if not result:
            print(f"Book '{book_name}' not found.")
            return None
        book_id = result[0]
        # Find the chapter_id for the given chapter number
        cursor.execute("SELECT id FROM chapter WHERE book_id = ? AND chapter_num = ?", (book_id, chapter))
        chap_result = cursor.fetchone()
        if not chap_result:
            print(f"Chapter {chapter} not found for book '{book_name}'.")
            return None
        chapter_id = chap_result[0]
        # Find the verse text
        cursor.execute("SELECT text FROM verse WHERE chapter_id = ? AND verseno = ?", (chapter_id, verse_num))
        verse_row = cursor.fetchone()
        if verse_row:
            return verse_row[0]
        else:
            print(f"Verse not found for {book_name} {chapter}:{verse_num}.")
            return None
    except Exception as e:
        print(f"Error gettingspecific verse: {e}")
        return None
    finally:
        conn.close()
def get_books():
    """Return a list of (id, book_name) for all books in the database (from 'book' table)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, book_name FROM book")
        books = []
        for book_id, book_name in cursor.fetchall():
            if book_name.startswith("Volume "):
                vol_num = book_name.split(" ")[-1]
                book_name = f"Articles of Faith Vol. {vol_num}"
            books.append((book_id, book_name))
    except Exception as e:
        print(f"Error getting books: {e}")
        books = []
    conn.close()
    return books

def get_random_quote(book_id):
    """Return a random verse text from the given book_id (from 'verse' table)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT text FROM verse WHERE book_id = ?", (book_id,))
        verses = cursor.fetchall()
        if verses:
            return random.choice(verses)[0]
        else:
            return None
    except Exception as e:
        print(f"Error with getting verses: {e}")
        return None
    finally:
        conn.close()
def get_all_verses():
    """Return list[dict] with text/book/chapter/verse for every verse."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT v.text, c.chapter_num, b.book_name, v.verseno FROM verse v JOIN chapter c ON v.chapter_id = c.id JOIN book b ON c.book_id = b.id")
        rows = cur.fetchall()
        out = []
        for text, chapter_num, book_name, verseno in rows:
            display_name = book_name
            if book_name.startswith("Volume "):
                vol_num = book_name.split(" ")[-1]
                display_name = f"Articles of Faith Vol. {vol_num}"
            out.append({"text": text, "book": display_name, "chapter": chapter_num, "verse": verseno})
        return out
    finally:
        conn.close()

def search_verses_struct(word: str):
    """Return list[dict] of verses that contain exact word (case-insensitive)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT v.text, c.chapter_num, b.book_name, v.verseno "
            "FROM verse v JOIN chapter c ON v.chapter_id = c.id JOIN book b ON c.book_id = b.id "
            "WHERE LOWER(v.text) LIKE ?",
            (f"%{word.lower()}%",)
        )
        rows = cur.fetchall()
        word_re = re.compile(rf'(?<!\w){re.escape(word)}(?!\w)', re.IGNORECASE)
        out = []
        for text, chapter_num, book_name, verseno in rows:
            if word_re.search(text):
                display_name = book_name
                if book_name.startswith("Volume "):
                    vol_num = book_name.split(" ")[-1]
                    display_name = f"Articles of Faith Vol. {vol_num}"
                out.append({"text": text, "book": display_name, "chapter": chapter_num, "verse": verseno})
        return out
    finally:
        conn.close()

def get_scriptures():
    """Alias used by the app to load all scriptures (list of strings)."""
    return get_all_verses()

if __name__ == "__main__":
    build_database()

    # Prompt user for a word to search in all verses
    while True:
        word = input("What would you like to search for? ").strip()
        if not word:
            print("Please enter a word to search for.")
            continue
        search_verses_by_word(word)
        print("\n---\n")
