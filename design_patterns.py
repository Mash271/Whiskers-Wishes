import sqlite3
import os
from abc import ABC, abstractmethod
from functools import wraps
from dotenv import load_dotenv
from flask import session
import psycopg2
# ==========================================
# 1. SINGLETON PATTERN (Database Connection)
# ==========================================
import psycopg2 # Make sure to import this!

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            print("[Singleton] Creating new DatabaseConnection instance.")
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
# 5. OBSERVER PATTERN (Application Status)
# ==========================================
class Observer(ABC):
    @abstractmethod
    def update(self, status, message=None):
        pass

class AdoptionSubject:
    """
    The 'Subject' that maintains a list of observers (users) and notifies them.
    """
    def __init__(self, app_id):
        self.app_id = app_id
        self._observers = []
        self._status = "Pending"

    def attach(self, observer):
        self._observers.append(observer)

    def process_decision(self, new_status, rejection_reason=None):
        self._status = new_status
        self.notify(rejection_reason)

    def notify(self, reason=None):
        print(f"\n[Observer Pattern Triggered] Processing Application #{self.app_id} -> {self._status}")
        for observer in self._observers:
            observer.update(self._status, reason)

# Concrete Observer: User Notification System
class UserNotificationObserver(Observer):
    def __init__(self, username, email, user_type):
        self.username = username
        self.email = email
        self.user_type = user_type

    def update(self, status, reason=None):
        # Logic: 
        # 1. Notify BOTH Adopter and Foster if 'Approved'
        # 2. Notify ONLY Adopter if 'Rejected' (with reason)
        
        if status == "Approved":
            print(f"📧 EMAIL TO {self.user_type.upper()} ({self.email}): "
                  f"Great news, {self.username}! The adoption has been APPROVED.")
        
        elif status == "Rejected" and self.user_type == "adopter":
             print(f"📧 EMAIL TO ADOPTER ({self.email}): "
                   f"Dear {self.username}, your adoption request was declined. Reason: {reason}")


