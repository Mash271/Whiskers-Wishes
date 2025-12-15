import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_db():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Error: DATABASE_URL not found in .env file")
        return

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        
        # Paste your schema here directly or read from file
        schema_commands = """
        -- 1. Users Table
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            profile_info TEXT,
            user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('admin', 'adopter', 'foster'))
        );

        -- 2. Admin Table
        CREATE TABLE IF NOT EXISTS admin (
            admin_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        -- 3. Foster Users Table
        CREATE TABLE IF NOT EXISTS foster_users (
            foster_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        -- 4. Adopters Table
        CREATE TABLE IF NOT EXISTS adopters (
            adopter_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            passport_number VARCHAR(30),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        -- 5. Cats Table
        CREATE TABLE IF NOT EXISTS cats (
            cat_id SERIAL PRIMARY KEY,
            foster_id INTEGER NOT NULL,
            name VARCHAR(50) NOT NULL,
            age INTEGER,
            breed VARCHAR(50),
            image_url VARCHAR(255),
            bio TEXT,
            vaccination_status VARCHAR(50) DEFAULT 'Not Vaccinated',
            application_status VARCHAR(50) DEFAULT 'Available',
            FOREIGN KEY (foster_id) REFERENCES foster_users(foster_id) ON DELETE CASCADE
        );

        -- 6. Cat Photos Table
        CREATE TABLE IF NOT EXISTS cat_photos (
            photo_id SERIAL PRIMARY KEY,
            cat_id INTEGER NOT NULL,
            photo_url VARCHAR(255) NOT NULL,
            FOREIGN KEY (cat_id) REFERENCES cats(cat_id) ON DELETE CASCADE
        );

        -- 7. Adoption Applications Table
        CREATE TABLE IF NOT EXISTS adoption_applications (
            application_id SERIAL PRIMARY KEY,
            adopter_id INTEGER NOT NULL,
            cat_id INTEGER NOT NULL,
            vaccination_fee DECIMAL(10, 2),
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            questionnaire_responses TEXT,
            application_status VARCHAR(20) DEFAULT 'Pending',
            FOREIGN KEY (adopter_id) REFERENCES adopters(adopter_id) ON DELETE CASCADE,
            FOREIGN KEY (cat_id) REFERENCES cats(cat_id) ON DELETE CASCADE
        );
        """
        
        cur.execute(schema_commands)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Success! Tables created in Neon database.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    init_db()