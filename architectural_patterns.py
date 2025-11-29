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
                cat_data['age'] = f"{cat_data['age']} years old" 
                
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
            
# --- Other Repositories would go here ---
# class UserRepository:
#     def __init__(self, db_conn):
#         self.conn = db_conn
#     
#     def create_user(self, data):
#         # ... SQL for user creation ...
#         pass