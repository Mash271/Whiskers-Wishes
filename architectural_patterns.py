import psycopg2
from design_patterns import DatabaseConnection
class CatRepository:
    """
    Implements the Repository Pattern, acting as the Data Access Layer (DAL) 
    for all Cat-related operations (CRUD).
    
    This abstracts the database logic (SQL, psycopg2 details) away from the 
    application's core business logic (app.py).
    """
        

    def get_available_cats(self):
        self.conn = DatabaseConnection().get_connection()
        print("entered get_all_cats in catrepository 1️⃣")
        """
        Fetches all cats from the database whose application_status is not 'Adopted'.
        
        Returns:
            list: A list of dictionaries, where each dictionary represents an available cat.
        """
        try:
            cur = self.conn.cursor()
            print("entered get_available_cats 2️⃣")
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
            print("3️⃣ about to enter loop to convert into list of dicts in catrepo getavailablecats")

            # Define column names explicitly for easy dictionary creation
            column_names = ['id', 'name', 'age', 'breed', 'story', 'status']

            # Convert records into a list of dictionaries for easy rendering in Flask/Jinja
            cats_list = []
            for record in cat_records:
                print("4️⃣ entered loop in catrepository")
                cat_data = dict(zip(column_names, record))
                print("4️5️⃣ executed zip in getavailablecats in catrepository")
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
    
    def create_user(self, username, email, password, full_name, user_type):
        """
        Creates a new user in the database.
        Returns the new user_id if successful, or None if failed.
        """
        self.conn = DatabaseConnection().get_connection()
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
        self.conn = DatabaseConnection().get_connection()
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
        
    def get_user_by_id(self, user_id):
        """Fetches a user record by user ID."""
        self.conn = DatabaseConnection().get_connection()
        try:
            cur = self.conn.cursor()
            
            # CRITICAL FIX: Use placeholder correctly and pass parameters separately
            query = f"""
                SELECT user_id, username, user_type, full_name, email 
                FROM users 
                WHERE user_id = {self.placeholder}
            """
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            cur.close()
            if row:
                return {"id": row[0], "username": row[1], "role": row[2], "full_name": row[3], "email": row[4]}
            return None
        except Exception as e:
            print(f"Error fetching user by id: {e}")
            return None
        
    

# NEW: Repository specifically for Admin tasks
class AdminRepository:
    """Repository for administrative data fetching and modification."""
    
    def get_all_users(self):
        self.conn = DatabaseConnection().get_connection()
        """Fetches all users except admins, excludes passwords."""
        try:
            print("entered get_all_users in adminrepository")
            cur = self.conn.cursor()
            query = """
                SELECT user_id, full_name, username, email, user_type 
                FROM users 
                WHERE user_type != 'admin'
            """
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            users = []
            for row in rows:
                users.append({
                    "id": row[0], "full_name": row[1], "username": row[2], 
                    "email": row[3], "role": row[4]
                })
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def get_pending_applications(self):
        self.conn = DatabaseConnection().get_connection()
        """Joins Applications, Users, and Cats to get full details for pending apps."""
        try:
            cur = self.conn.cursor()
            # The query is complex because of the separation into `adopters` table
            query = """
                SELECT 
                    a.application_id, u.full_name, c.name, a.application_status, a.cat_id, u.user_id
                FROM adoption_applications a
                JOIN adopters d ON a.adopter_id = d.adopter_id
                JOIN users u ON d.user_id = u.user_id
                JOIN cats c ON a.cat_id = c.cat_id
                WHERE a.application_status = 'Pending'
            """
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            apps = []
            for row in rows:
                apps.append({
                    "app_id": row[0], "applicant_name": row[1], "cat_name": row[2], 
                    "status": row[3], "cat_id": row[4], "user_id": row[5] # user_id is the main users.user_id
                })
            return apps
        except Exception as e:
            print(f"Error getting pending applications: {e}")
            return []
    
    def get_application_details(self, app_id):
        self.conn = DatabaseConnection().get_connection()
        """Gets deep details for the processing page by application ID."""
        try:
            cur = self.conn.cursor()
            
            # Query to fetch all necessary details
            query = f"""
                SELECT 
                    a.application_id, 
                    u.full_name, u.email, u.user_type, 
                    c.name, c.breed, c.age, c.image_url, 
                    a.application_status, 
                    c.cat_id, 
                    u.user_id
                FROM adoption_applications a
                JOIN adopters d ON a.adopter_id = d.adopter_id
                JOIN users u ON d.user_id = u.user_id
                JOIN cats c ON a.cat_id = c.cat_id
                WHERE a.application_id = {self.placeholder}
            """
            cur.execute(query, (app_id,))
            row = cur.fetchone()
            cur.close()
            if row:
                return {
                    "id": row[0], "applicant_name": row[1], "applicant_email": row[2],
                    "applicant_role": row[3], "cat_name": row[4], "cat_breed": row[5],
                    "cat_age": row[6], "cat_image": row[7], "status": row[8],
                    "cat_db_id": row[9], "user_db_id": row[10]
                }
            return None
        except Exception as e:
            print(f"Error getting application details: {e}")
            return None

    def update_application_status(self, app_id, new_status, reason=None):
        """Updates the status of an application and the related cat status if approved."""
        self.conn = DatabaseConnection().get_connection()
        try:
            cur = self.conn.cursor()
            
            # 1. Update Application Status
            update_app_query = f"UPDATE adoption_applications SET application_status = {self.placeholder}, rejection_reason = {self.placeholder} WHERE application_id = {self.placeholder}"
            cur.execute(update_app_query, (new_status, reason, app_id))
            
            # 2. If Approved, update Cat's status
            if new_status == 'Approved':
                # First find the cat_id associated with the application
                find_cat_query = f"SELECT cat_id FROM adoption_applications WHERE application_id = {self.placeholder}"
                cur.execute(find_cat_query, (app_id,))
                cat_id = cur.fetchone()[0]
                
                # Update Cat status
                update_cat_query = f"UPDATE cats SET application_status = 'Adopted' WHERE cat_id = {self.placeholder}"
                cur.execute(update_cat_query, (cat_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating application status: {e}")
            self.conn.rollback()
            return False