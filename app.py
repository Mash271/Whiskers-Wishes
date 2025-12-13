import os
from flask import Flask, render_template, request, redirect, flash, url_for, session
from dotenv import load_dotenv
from datetime import datetime
from architectural_patterns import CatRepository, UserRepository, AdminRepository

# Import your design patterns
from design_patterns import (
    DatabaseConnection, 
    CatBuilder, 
    UserFactory,
    mock_session, 
    admin_required,
    AdoptionSubject,
    UserNotificationObserver
)

# Load environment variables from .env file
#this line was commented until now, maybe this is why the
# database connection was failing?
load_dotenv()

app = Flask(__name__)
app.secret_key = "dont_tell_anyone_my_secret"

# --- DATABASE SETUP (SINGLETON PATTERN) ---
# We initialize the connection once. 
# Even if we call this multiple times, it returns the same connection instance.
db_conn = DatabaseConnection().get_connection()
if db_conn is None:
    raise RuntimeError("❌ CRITICAL ERROR: Could not connect to the database. Check your DATABASE_URL and logs.")
else:
    print("✅ Database connection established successfully.")


# Function to get available cats using the CatRepository
def get_available_cats(db_conn):
    cat_repo = CatRepository(db_conn)
    return cat_repo.get_available_cats()



# This route maps the root URL "/" to this function
@app.route("/")
def home():
    # --- DATA CREATION (BUILDER PATTERN) ---
    # Using the Builder Pattern to create complex Cat objects
    
    cat1 = (CatBuilder()
            .set_name("Mochi")
            .set_age("3 Months (Kitten)")
            .set_story("Found in a cardboard box during a storm, Mochi is a tiny survivor with a huge heart.")
            .set_status("Available")
            .set_image("https://images.unsplash.com/photo-1591871937573-74dbba515c4c?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTR8fGtpdHRlbnxlbnwwfHwwfHx8MA%3D%3D")
            .build())
    cat2 = (CatBuilder()
            .set_name("Luna")
            .set_age("4 Years (Adult)")
            .set_story("Luna is a calm, sophisticated lady who enjoys birdwatching from the window.")
            .set_status("Available")
            .set_image("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80")
            .build())
    cat3 = (CatBuilder()
            .set_name("Oscar Sr")
            .set_age("12 Years (Senior)")
            .set_story("Oscar is a wise soul who just wants a warm lap to sleep on.")
            .set_status("Urgent")
            .set_image("https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=400&q=80")
            .build())

    # Convert objects to dicts so Jinja template can render them easily
    # (assuming your HTML uses cat.name, cat.story, etc.)
    featured_cats = [cat1.to_dict(), cat2.to_dict(), cat3.to_dict()]
    return render_template("hello_there.html", 
                           featured_cats=featured_cats,
                           today=datetime.today().strftime("%A, %B %d, %Y"),
                           date=datetime.now(),
                           name=None)
    #..
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
    return render_template("admin.html", user=session.get("username"))

# --- NAVIGATION LINKS DEMONSTRATION ---
# 2. Gallery Link -> href="{{ url_for('gallery') }}"
@app.route("/gallery")
def gallery():
    # 1. Fetch the data from the database
    available_cats = get_available_cats(db_conn)
    
    # 2. Pass the filtered data to the template
    return render_template("gallery.html", cats=available_cats)

# 3. About Link -> href="{{ url_for('about') }}"
@app.route("/about")
def about():
    return render_template("about.html")

# ==========================================
# AUTH ROUTES
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        #......
        # Hardcoded Admin Backdoor
        if username == "Admin" and password == "67890":
            session["user_id"] = 0
            session["username"] = "Admin"
            session["role"] = "admin"
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        # Database Login
        repo = UserRepository()
        user = repo.get_user_by_username(username)
        
        if user and user['password'] == password:
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["logged_in"] = True
            
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("home"))
            
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/admin")
@admin_required
def admin_dashboard():
    # Main Menu
    return render_template("admin.html", user=session.get("username"))

@app.route("/admin/users")
@admin_required
def admin_users():
    repo = AdminRepository()
    users = repo.get_all_users()
    #print users

    return render_template("admin_users.html", users=users)

@app.route("/admin/cats")
@admin_required
def admin_cats():
    # Reusing CatRepository to get inventory
    repo = CatRepository(conn=db_conn)
    # We ideally want ALL cats, even adopted ones, but for now we use available
    cats = repo.get_available_cats()
        
    return render_template("admin_cats.html", cats=cats)

@app.route("/admin/applications")
@admin_required
def admin_applications():
    repo = AdminRepository() #new adminrepository() object to call its functions
    apps = repo.get_pending_applications()
    return render_template("admin_applications.html", applications=apps)

@app.route("/admin/process/<int:app_id>", methods=["GET", "POST"])
@admin_required
def admin_process_adoption(app_id):
    repo = AdminRepository()
    
    if request.method == "POST":
        action = request.form.get("action") # 'approve' or 'decline'
        reason = request.form.get("reason", "")
        
        # 1. Fetch details to setup Observers
        details = repo.get_application_details(app_id)
        if not details:
            return "Application not found", 404

        # 2. Setup Observer Pattern
        adoption_subject = AdoptionSubject(app_id)
        
        # Add Adopter Observer
        adopter_observer = UserNotificationObserver(details['applicant_name'], details['applicant_email'], "adopter")
        adoption_subject.attach(adopter_observer)
        
        # Add Foster Observer (Mocking a generic foster for now, or fetching if we had one)
        foster_observer = UserNotificationObserver("Foster Parent", "foster@example.com", "foster")
        adoption_subject.attach(foster_observer)

        # 3. Process Logic
        if action == "approve":
            # Update DB
            success = repo.update_application_status(app_id, "Approved")
            if success:
                # Trigger Observers
                adoption_subject.process_decision("Approved")
                flash("Adoption Approved! Emails sent.", "success")
            else:
                flash("Database Error.", "error")
                
        elif action == "decline":
            if not reason:
                return "Error: Rejection reason required.", 400
            
            # Update DB
            repo.update_application_status(app_id, "Rejected", reason)
            # Trigger Observers
            adoption_subject.process_decision("Rejected", reason)
            flash("Adoption Declined. Applicant notified.", "warning")

        return redirect(url_for("admin_applications"))

    # GET Request: Show form
    details = repo.get_application_details(app_id)
    return render_template("admin_process_adoption.html", app=details)


@app.route("/logout")
def logout():
    session.clear() # Wipes the cookie
    return redirect(url_for("home"))

# 5. Register Link -> href="{{ url_for('register') }}"
# Inside app.py

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 1. Get data from the HTML form
        user_type = request.form.get("role")
        
        # Get the username directly from the form
        username = request.form.get("username") 
        
        # (Delete the old line that said: username = email.split("@")[0])

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # 2. Validation
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match!")

        # 3. Save to Database
        user_repo = UserRepository(db_conn)

        # Check if username ALREADY exists
        if user_repo.get_user_by_username(username):
            return render_template("register.html", error="That username is already taken!")

        # Create the user
        new_id = user_repo.create_user(username, email, password, full_name, user_type)
        
        if new_id:
            print(f"✅ User Created: {username} (ID: {new_id})")
            return redirect(url_for('login'))
        else:
            return render_template("register.html", error="Registration failed. Username or Email might be taken.")

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)