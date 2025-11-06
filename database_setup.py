import sqlite3

# ---------------------------
# DATABASE INITIALIZATION
# ---------------------------

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create users table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            lang TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database and 'users' table initialized successfully.")

# ---------------------------
# INSERT SAMPLE DATA (OPTIONAL)
# ---------------------------

def insert_sample_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    users = [
        ("amit", "12345", "en"),
        ("prathamesh", "abcde", "hi"),
        ("karishma", "xyz123", "mr")
    ]

    for u in users:
        try:
            c.execute('INSERT INTO users(username, password, lang) VALUES (?, ?, ?)', u)
        except sqlite3.IntegrityError:
            print(f"Warning: User '{u[0]}' already exists, skipping.")


    conn.commit()
    conn.close()
    print("✅ Sample users inserted successfully.")

# ---------------------------
# FETCH ALL USERS (FOR TESTING)
# ---------------------------

def view_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    conn.close()

    print("📋 Current Users in Database:")
    for row in data:
        print(row)

# ---------------------------
# MAIN EXECUTION
# ---------------------------

if __name__ == "__main__":
    init_db()
    insert_sample_users()   # Optional — comment out if not needed
    view_all_users()
