import os
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import datetime

# Import your design patterns
from design_patterns import (
    DatabaseConnection, 
    CatBuilder, 
    UserFactory, 
    mock_session, 
    admin_required
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- DATABASE SETUP (SINGLETON PATTERN) ---
# We initialize the connection once. 
# Even if we call this multiple times, it returns the same connection instance.
db_conn = DatabaseConnection().get_connection()


# This route maps the root URL "/" to this function
@app.route("/")
def home():
    # --- DATA CREATION (BUILDER PATTERN) ---
    # Using the Builder Pattern to create complex Cat objects
    # replacing the manual dictionary creation you had before.
    
    cat1 = (CatBuilder()
            .set_name("Mochi")
            .set_age("3 Months (Kitten)")
            .set_story("Found in a cardboard box during a storm, Mochi is a tiny survivor with a huge heart.")
            .set_status("Available")
            .set_image("https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=400&q=80")
            .build())

    cat2 = (CatBuilder()
            .set_name("Luna")
            .set_age("4 Years (Adult)")
            .set_story("Luna is a calm, sophisticated lady who enjoys birdwatching from the window.")
            .set_status("Available")
            .set_image("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80")
            .build())

    cat3 = (CatBuilder()
            .set_name("Oscar")
            .set_age("12 Years (Senior)")
            .set_story("Oscar is a wise soul who just wants a warm lap to sleep on.")
            .set_status("Urgent")
            .set_image("https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=400&q=80")
            .build())

    # Convert objects to dicts so Jinja template can render them easily
    # (assuming your HTML uses cat.name, cat.story, etc.)
    featured_cats = [cat1.to_dict(), cat2.to_dict(), cat3.to_dict()]

    return render_template("landing_page.html", 
                         featured_cats=featured_cats,
                         today=datetime.today().strftime("%A, %B %d, %Y"))

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

# --- DEMONSTRATION OF DECORATOR PATTERN ---
@app.route("/admin")
@admin_required
def admin_panel():
    return "<h1>Welcome to the Secret Admin Panel!</h1><p>You can only see this if logged in as Admin.</p>"

# Route to simulate logging in (for testing the decorator)
@app.route("/login-admin")
def login_test():
    mock_session["is_logged_in"] = True
    mock_session["user_role"] = "Admin"
    return "You are now logged in as Admin. Try visiting <a href='/admin'>/admin</a>"

# 1. Home Link -> href="{{ url_for('home') }}"
@app.route("/")
def home():
    # ... logic ...
    return render_template("landing_page.html", ...)

# 2. Gallery Link -> href="{{ url_for('gallery') }}"
@app.route("/gallery")
def gallery():
    # ... logic ...
    return render_template("gallery.html", ...)

# 3. About Link -> href="{{ url_for('about') }}"
@app.route("/about")
def about():
    return render_template("about.html")

# 4. Login Link -> href="{{ url_for('login') }}"
@app.route("/login", methods=["GET", "POST"])
def login():
    # ... logic ...
    return render_template("login.html")

# 5. Register Link -> href="{{ url_for('register') }}"
@app.route("/register")
def register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)