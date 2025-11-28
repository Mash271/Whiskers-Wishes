-- 1. Users Table (Base table for all user types)
-- Stores common login and profile information [cite: 432, 433, 434, 435, 436, 437, 438, 439]
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    profile_info TEXT,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('admin', 'adopter', 'foster'))
);

-- 2. Admin Table
-- Links to users table, specific to Admin role [cite: 457, 458]
CREATE TABLE admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Foster Users Table
-- Links to users table, for users who post cats [cite: 461, 464]
CREATE TABLE foster_users (
    foster_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Adopters Table
-- Links to users table, includes specific fields like passport_number [cite: 459, 460, 465]
CREATE TABLE adopters (
    adopter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    passport_number VARCHAR(30),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. Cats Table
-- Stores cat profiles created by foster users [cite: 443, 444, 445, 446, 448, 449, 451, 452, 455]
CREATE TABLE cats (
    cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    foster_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    age INTEGER,
    breed VARCHAR(50),
    bio TEXT,
    vaccination_status VARCHAR(50) DEFAULT 'Not Vaccinated',
    application_status VARCHAR(50) DEFAULT 'Available',
    FOREIGN KEY (foster_id) REFERENCES foster_users(foster_id) ON DELETE CASCADE
);

-- 6. Cat Photos Table
-- Stores URLs for images associated with a specific cat [cite: 467, 468, 472]
CREATE TABLE cat_photos (
    photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_id INTEGER NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (cat_id) REFERENCES cats(cat_id) ON DELETE CASCADE
);

-- 7. Adoption Applications Table
-- Connects an Adopter to a Cat with status and fees [cite: 469, 470, 474, 475, 477, 479, 480, 481]
CREATE TABLE adoption_applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    adopter_id INTEGER NOT NULL,
    cat_id INTEGER NOT NULL,
    vaccination_fee DECIMAL(10, 2),
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    questionnaire_responses TEXT,
    application_status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (adopter_id) REFERENCES adopters(adopter_id) ON DELETE CASCADE,
    FOREIGN KEY (cat_id) REFERENCES cats(cat_id) ON DELETE CASCADE
);