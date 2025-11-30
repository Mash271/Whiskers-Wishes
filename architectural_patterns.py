import psycopg2

class CatRepository:
    """
    Implements the Repository Pattern, acting as the Data Access Layer (DAL) 
    for all Cat-related operations (CRUD).
    
    This abstracts the database logic (SQL, psycopg2 details) away from the 
    application's core business logic (app.py).
    """
    def __init__(self, db_conn):
        """Initializes the repository with a database connection."""
        self.conn = db_conn

    def get_available_cats(self):
        """
        Fetches all cats from the database whose application_status is not 'Adopted'.
        
        Returns:
            list: A list of dictionaries, where each dictionary represents an available cat.
        """
        try:
            cur = self.conn.cursor()
            
            # SQL Query to select cats that are not adopted
            sql_query = """
                SELECT 
                    cat_id, 
                    name, 
                    age, 
                    breed, 
                    bio, 
                    application_status
                FROM cats
                WHERE application_status != 'Adopted'
                ORDER BY cat_id;
            """
            cur.execute(sql_query)
            cat_records = cur.fetchall()
            cur.close()

            # Define column names explicitly for easy dictionary creation
            column_names = ['id', 'name', 'age', 'breed', 'story', 'status']

            # Convert records into a list of dictionaries for easy rendering in Flask/Jinja
            cats_list = []
            for record in cat_records:
                cat_data = dict(zip(column_names, record))
                
                # Temporary addition of a placeholder image (as we don't have cat_photos join yet)
                cat_data['image'] = f"https://placehold.co/400x200/50c4db/white?text={cat_data['name']}"
                
                # NOTE: Age is an integer in the DB, converting for the template display
                cat_data['age'] = f"{cat_data['age']}" 
                
                cats_list.append(cat_data)
                
            return cats_list

        except psycopg2.Error as e:
            print(f"❌ Database Error in CatRepository: {e}")
            if self.conn and hasattr(self.conn, 'in_transaction') and self.conn.in_transaction:
                self.conn.rollback()
            return []
        except Exception as e:
            print(f"❌ General Error in CatRepository: {e}")
            return []
            
# In architectural_patterns.py

class UserRepository:
    def __init__(self, db_conn):
        self.conn = db_conn

    # ... existing get_user_by_username method ...

    def create_user(self, username, email, password, full_name, user_type):
        """
        Creates a new user in the database.
        Returns the new user_id if successful, or None if failed.
        """
        try:
            cur = self.conn.cursor()
            
            # SQL Query for PostgreSQL
            # Note: We are inserting into 'users'. 
            # Ideally, we should also insert into 'adopters' or 'foster_users' tables 
            # based on user_type, but let's start with the base user.
            query = """
                INSERT INTO users (username, email, hashed_password, full_name, user_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id;
            """
            
            # Executing the query
            cur.execute(query, (username, email, password, full_name, user_type))
            
            # Commit the transaction (Save changes)
            self.conn.commit()
            
            # Get the generated ID
            new_user_id = cur.fetchone()[0]
            cur.close()
            
            return new_user_id

        except Exception as e:
            print(f"❌ Error creating user: {e}")
            self.conn.rollback() # Undo changes if error
            return None
        
    def get_user_by_username(self, username):
        """
        Fetches a user record by their username.
        Returns a dictionary containing user details or None if not found.
        """
        try:
            cur = self.conn.cursor()
            
            # Select the password (hash) and role (user_type) to verify login
            query = """
                SELECT user_id, username, hashed_password, user_type, full_name 
                FROM users 
                WHERE username = %s
            """
            
            cur.execute(query, (username,))
            record = cur.fetchone()
            cur.close()

            if record:
                # Map the database tuple to a dictionary for easy access in app.py
                return {
                    "user_id": record[0],
                    "username": record[1],
                    "password": record[2],  # This matches user_data['password'] in app.py
                    "role": record[3],      # This matches user_data['role'] in app.py
                    "full_name": record[4]
                }
            return None

        except Exception as e:
            print(f"❌ Error fetching user: {e}")
            # Ensure we don't leave a transaction open if something breaks
            if self.conn:
                self.conn.rollback()
            return None