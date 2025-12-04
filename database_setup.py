import sqlite3

DB_PATH = "users.db"

# ---------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- USERS TABLE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            lang TEXT
        )
    """)

    # --- HISTORY TABLE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            query TEXT,
            actions TEXT,
            proofs TEXT,
            win INTEGER,
            timestamp TEXT
        )
    """)

    # --- SAFELY ADD NEW COLUMNS ---
    # Add IPC column
    try:
        c.execute("ALTER TABLE history ADD COLUMN ipc TEXT")
    except:
        pass

    # Add TS column (for display sorting)
    try:
        c.execute("ALTER TABLE history ADD COLUMN ts TEXT")
    except:
        pass

    conn.commit()
    conn.close()
    print("✅ Database initialized with all required tables and columns.")


# ---------------------------------------------
# INSERT SAMPLE DATA (OPTIONAL)
# ---------------------------------------------
def insert_sample_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    users = [
        ("amit", "12345", "en"),
        ("prathamesh", "abcde", "hi"),
        ("karishma", "xyz123", "mr")
    ]

    for u in users:
        try:
            c.execute(
                "INSERT INTO users(username, password, lang) VALUES (?, ?, ?)", 
                u
            )
        except sqlite3.IntegrityError:
            print(f"⚠️ User '{u[0]}' already exists. Skipping.")

    conn.commit()
    conn.close()
    print("✅ Sample users inserted successfully.")


# ---------------------------------------------
# FETCH ALL USERS (TESTING)
# ---------------------------------------------
def view_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()

    print("📋 Current Users:")
    for r in rows:
        print(r)


# ---------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------
if __name__ == "__main__":
    init_db()
    insert_sample_users()   # optional
    view_all_users()
