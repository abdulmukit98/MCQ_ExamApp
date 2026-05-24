import sqlite3

# Create/connect database
conn = sqlite3.connect("mcq.db")

# Create cursor
cursor = conn.cursor()

# Create questions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL
)
""")

# Save changes
conn.commit()

# Close connection
conn.close()

print("Database and table created successfully.")

