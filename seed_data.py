#this is where i hardcode some seed data for the database
import os
import psycopg2
from dotenv import load_dotenv
from design_patterns import CatBuilder # Reuse your builder pattern
from werkzeug.security import generate_password_hash # Used for dummy user password

# Load environment variables (including DATABASE_URL)
load_dotenv()

# --- 1. DEFINE DATA TO INSERT ---

# Note: We must insert a foster user first to get a valid foster_id.
DUMMY_PASSWORD = generate_password_hash("password123") 
FOSTER_USER_DATA = {
    "username": "admin_foster",
    "email": "foster@whiskerswishes.com",
    "password": DUMMY_PASSWORD,
    "user_type": "foster",
    "full_name": "Admin Foster"
}

# The sample cats data using your CatBuilder
# We are simplifying 'age' to an INTEGER for the DB.
cats_data = [
    (CatBuilder()
        .set_name("Mochi")
        .set_age(3) # Simplified to integer
        .set_breed("Domestic Shorthair")
        .set_story("Found in a cardboard box during a storm, Mochi is a tiny survivor with a huge heart.")
        .set_status("Available")
        .set_image("https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=400&q=80")
        .build()),
    (CatBuilder()
        .set_name("Luna")
        .set_age(4) # Simplified to integer
        .set_breed("Calico")
        .set_story("Luna is a calm, sophisticated lady who enjoys birdwatching from the window.")
        .set_status("Available")
        .set_image("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80")
        .build()),
    (CatBuilder()
        .set_name("Oscar")
        .set_age(12) # Simplified to integer
        .set_breed("Tuxedo")
        .set_story("Oscar is a wise soul who just wants a warm lap to sleep on.")
        .set_status("Urgent")
        .set_image("https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=400&q=80")
        .build()),
]

# --- 2. DATABASE INSERTION LOGIC ---

def seed_data():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("❌ Error: DATABASE_URL not found. Ensure your .env file is set up.")
        return

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()

        print("Connected to NeonDB. Starting data insertion...")

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
        # This foster_id is required for the cats table
        foster_id = cur.fetchone()[0] 
        print(f"   ✅ Foster User (ID: {foster_user_id}) and Foster Link (ID: {foster_id}) created.")

        # --- B. INSERT CATS ---
        cat_insert_sql = """
            INSERT INTO cats (foster_id, name, age, breed, bio, application_status)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        inserted_count = 0
        for cat in cats_data:
            cur.execute(cat_insert_sql, (
                foster_id,              # foster_id (from above)
                cat.name,               # name
                cat.age,                # age (integer)
                cat.breed,              # breed
                cat.story,              # story maps to bio column
                cat.status              # application_status
            ))
            inserted_count += 1
            
        conn.commit()
        print(f"   ✅ Successfully inserted {inserted_count} sample cats.")

    except Exception as e:
        print(f"❌ An error occurred during seeding: {e}")
        # Rollback in case of error
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        # Always close the connection
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    # You must run init_db.py at least once before running this script!
    seed_data()