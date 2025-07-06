import sqlite3

DATABASE_PATH = "mcp_analysis_data.db"

def connect_to_database() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_PATH)

def init_database():
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repository (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_name TEXT,
                full_path TEXT,
                filename TEXT,
                classification TEXT,
                language TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT,            -- Π.χ. 'X' ή '9' από το Picture Clause
                size INTEGER,         -- Το μήκος του πεδίου
                sudoType TEXT,        -- Τύπος σε μορφή ψευδοκώδικα για κατανόηση
                FOREIGN KEY (repository_id) REFERENCES repository(id)
            )
        """)
        conn.commit()
        print("Database initialized")

def insert_repository(repository_name: str, full_path: str, filename: str, language: str, classification: str):
    try:
        with connect_to_database() as conn:
            conn.execute("""
                INSERT INTO repository (repository_name, full_path, filename, language, classification)
                VALUES (?, ?, ?, ?, ?)
            """, (repository_name, full_path, filename, language, classification))
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def get_repository(repository_name: str):
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repository WHERE repository_name = ?", (repository_name,))
        return cursor.fetchall()

def get_all_repositories():
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repository")
        return cursor.fetchall()

def get_repository_by_filename(filename: str):
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repository WHERE filename = ?", (filename,))
        return cursor.fetchall()

def get_repository_by_classification(classification: str, repository_name: str):
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repository WHERE classification = ? AND repository_name = ?", (classification, repository_name))
        return cursor.fetchall()

def get_file_full_path(repository_name: str, filename: str):
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_path FROM repository WHERE repository_name = ? AND filename = ?", (repository_name, filename))
        return cursor.fetchone()

