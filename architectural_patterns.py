# Updated Architectural Pattern Implementations
# This file now excludes the Singleton pattern (moved to design_patterns.py as per project structure).
# Comments are included to clarify why each section exists or was modified.

# Example Repository Layer Pattern
class UserRepository:
    def __init__(self, db_singleton):
        # db_singleton must be an instance retrieved through the Singleton accessor
        self.db = db_singleton

    def get_user(self, user_id):
        # Typical repository behavior: isolate raw database operations
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()


# Example Service Layer Pattern
class UserService:
    def __init__(self, user_repo):
        # Service depends on repository but does not access DB directly
        self.user_repo = user_repo

    def fetch_user_profile(self, user_id):
        # Encapsulate business logic separately from repository logic
        return self.user_repo.get_user(user_id)


# Controller Layer (optional addition)
# Illustrates how controllers should call services instead of repositories
class UserController:
    def __init__(self, user_service):
        self.user_service = user_service

    def get_profile(self, user_id):
        # A clean controller-service-repository flow
        return self.user_service.fetch_user_profile(user_id)
