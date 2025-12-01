# seed_data.py

# ==========================================
# 1. IMPORTS
# ==========================================
import os
import psycopg2 # Used for the Render connection (if needed)
import sqlite3 # Used for the local connection (if needed)
from dotenv import load_dotenv
from design_patterns import CatBuilder 
from design_patterns import DatabaseConnection # <-- ⭐️ Import the Singleton Class
from werkzeug.security import generate_password_hash 

# Load environment variables
load_dotenv()

# --- 2. DEFINE DATA TO INSERT (Keep this section as is) ---

DUMMY_PASSWORD = generate_password_hash("password123") 
FOSTER_USER_DATA = {
    "username": "admin_foster",
    "email": "foster@whiskerswishes.com",
    "password": DUMMY_PASSWORD,
    "user_type": "foster",
    "full_name": "Admin Foster"
}

cats_data = [
    # Mochi, Luna, Oscar data (as you defined above)
    (CatBuilder().set_name("Mochi").set_age(3).set_breed("Domestic Shorthair").set_story("...").set_status("Available").set_image("...").build()),
    (CatBuilder().set_name("Luna").set_age(4).set_breed("Calico").set_story("...").set_status("Available").set_image("...").build()),
    (CatBuilder().set_name("Oscar").set_age(12).set_breed("Tuxedo").set_story("...").set_status("Urgent").set_image("...").build()),
]

# --- 3. DATABASE INSERTION LOGIC (Function now accepts conn object) ---

def seed_data(conn):
    """
    Inserts all hardcoded user and cat data into the provided database connection.
    """
    cur = None # Initialize cur for safe cleanup
    try:
        cur = conn.cursor()

        print(f"Connected to DB ({conn.info.host if isinstance(conn, psycopg2.extensions.connection) else 'SQLite'}). Starting data insertion...")

        # --- A. INSERT FOSTER USER ---
        # 1. Insert into users table
        user_insert_sql = """
            INSERT INTO users (username, email, hashed_password, full_name, user_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id;
        """
        cur.execute(user_insert_sql, (
            FOSTER_USER_DATA['username'],
            FOSTER_USER_DATA['email'],
            FOSTER_USER_DATA['password'],
            FOSTER_USER_DATA['full_name'],
            FOSTER_USER_DATA['user_type']
        ))
        foster_user_id = cur.fetchone()[0]
        
        # 2. Insert into foster_users table
        foster_insert_sql = """
            INSERT INTO foster_users (user_id) VALUES (%s) RETURNING foster_id;
        """
        cur.execute(foster_insert_sql, (foster_user_id,))
        foster_id = cur.fetchone()[0] 
        print(f"   ✅ Foster User (ID: {foster_user_id}) and Foster Link (ID: {foster_id}) created.")

        # --- B. INSERT CATS ---
        cat_insert_sql = """
            INSERT INTO cats (foster_id, name, age, breed, bio, application_status)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        inserted_count = 0
        for cat in cats_data:
            cur.execute(cat_insert_sql, (
                foster_id,          
                cat.name,           
                cat.age,            
                cat.breed,          
                cat.story,          
                cat.status          
            ))
            inserted_count += 1
            
        conn.commit()
        print(f"   ✅ Successfully inserted {inserted_count} sample cats.")

    except Exception as e:
        print(f"❌ An error occurred during seeding: {e}")
        # Rollback in case of error
        conn.rollback()
    finally:
        # Only close the cursor, do NOT close the connection if it's a Singleton
        if cur:
            cur.close()
        # print("Database connection (Singleton) kept open.") # Optional print

# --- 4. EXECUTION BLOCK (How to run this script standalone) ---

if __name__ == "__main__":
    # 1. Get the connection from the Singleton
    db_conn_instance = DatabaseConnection()
    conn = db_conn_instance.get_connection()

    # 2. Execute the seeding function
    seed_data(conn)

    print("\nSeeding script finished.")