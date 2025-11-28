import sqlite3
import os
from abc import ABC, abstractmethod
from functools import wraps
from dotenv import load_dotenv

# ==========================================
# 1. SINGLETON PATTERN (Database Connection)
# ==========================================
import psycopg2 # Make sure to import this!

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            
            # Check if we are on Render by looking for the DATABASE_URL variable
            db_url = os.environ.get("DATABASE_URL")

            if db_url:
                # We are on Render! Connect to Postgres
                cls._instance.connection = psycopg2.connect(db_url)
                print("[Singleton] Connected to Render PostgreSQL Database.")
            else:
                # We are local! Connect to SQLite
                cls._instance.connection = sqlite3.connect('whiskers_wishes.db', check_same_thread=False)
                print("[Singleton] Connected to Local SQLite Database.")

        return cls._instance

    def get_connection(self):
        return self.connection

# ==========================================
# 2. FACTORY METHOD PATTERN (User Creation)
# ==========================================
class User(ABC):
    @abstractmethod
    def get_role(self):
        pass

class Adopter(User):
    def get_role(self):
        return "Adopter"

class FosterCareUser(User):
    def get_role(self):
        return "Foster Care User"

class Admin(User):
    def get_role(self):
        return "Admin"

class UserFactory:
    @staticmethod
    def create_user(user_type):
        if user_type == "adopter":
            return Adopter()
        elif user_type == "foster":
            return FosterCareUser()
        elif user_type == "admin":
            return Admin()
        else:
            raise ValueError("Unknown user type")

# ==========================================
# 3. BUILDER PATTERN (Cat Profile Creation)
# ==========================================
class Cat:
    def __init__(self):
        # Updated to match the fields in your app.py
        self.name = None
        self.age = None
        self.story = None # Changed from 'bio' to 'story' to match your app
        self.status = "Available"
        self.image = None
        self.breed = None
        self.vaccinated = False

    # This allows the object to be converted to a dictionary for Jinja templates
    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "story": self.story,
            "status": self.status,
            "image": self.image,
            "breed": self.breed
        }

class CatBuilder:
    def __init__(self):
        self.cat = Cat()

    def set_name(self, name):
        self.cat.name = name
        return self

    def set_age(self, age):
        self.cat.age = age
        return self

    def set_story(self, story):
        self.cat.story = story
        return self

    def set_image(self, image_url):
        self.cat.image = image_url
        return self

    def set_status(self, status):
        self.cat.status = status
        return self

    def set_breed(self, breed):
        self.cat.breed = breed
        return self

    def build(self):
        return self.cat

# ==========================================
# 4. STRATEGY PATTERN (Filtering Cats)
# ==========================================
class FilterStrategy(ABC):
    @abstractmethod
    def filter(self, cats, criteria):
        pass

class AgeFilter(FilterStrategy):
    def filter(self, cats, age_limit):
        # Assumes 'cats' is a list of Cat objects
        return [cat for cat in cats if cat.age == age_limit]

class StatusFilter(FilterStrategy):
    def filter(self, cats, status):
        return [cat for cat in cats if cat.status == status]

class CatGallery:
    def __init__(self, cats):
        self.cats = cats
        self.strategy = None

    def set_strategy(self, strategy: FilterStrategy):
        self.strategy = strategy

    def get_filtered_cats(self, criteria):
        if not self.strategy:
            return self.cats
        return self.strategy.filter(self.cats, criteria)

# ==========================================
# 5. OBSERVER PATTERN (Application Status)
# ==========================================
class Observer(ABC):
    @abstractmethod
    def update(self, status):
        pass

class EmailNotification(Observer):
    def update(self, status):
        print(f"[Observer] Email sent: Your application status is now '{status}'.")

class CatStatusUpdater(Observer):
    def update(self, status):
        if status == "Approved":
            print("[Observer] System updated cat status to 'Adopted'.")

class AdoptionApplication:
    def __init__(self, applicant_name):
        self.applicant = applicant_name
        self._observers = []
        self._status = "Pending"

    def attach(self, observer):
        self._observers.append(observer)

    def set_status(self, new_status):
        self._status = new_status
        self.notify()

    def notify(self):
        for observer in self._observers:
            observer.update(self._status)

# ==========================================
# 6. DECORATOR PATTERN (Route Protection)
# ==========================================
# A global dictionary to simulate a logged-in user session
# You can modify this from app.py
mock_session = {"user_role": None, "is_logged_in": False}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not mock_session["is_logged_in"]:
            return "<h1>Access Denied: You must be logged in.</h1>", 403
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if mock_session["user_role"] != "Admin":
            return "<h1>Access Denied: Admins only.</h1>", 403
        return f(*args, **kwargs)
    return decorated_function