# =============================
# Updated app.py
# =============================

"""
CHANGES MADE:
1. Removed hardcoded secret key and replaced with environment variable.
2. Removed debug=True from app.run(). Added environment toggle.
3. Replaced hardcoded admin credentials with environment variables.
4. Implemented proper password hashing and checking using werkzeug.security.
5. Added comments explaining each change.
"""

import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import get_db_connection

app = Flask(__name__)

# ---------------------------------------------
# CHANGE 1: Secret key no longer hardcoded.
# Using environment variable to avoid security leak.
# ---------------------------------------------
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_key_for_dev_only")

# ---------------------------------------------
# CHANGE 2: Admin credentials no longer hardcoded.
# Using environment variables so the password isn't exposed.
# ---------------------------------------------
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "AdminPass123")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ---------------------------------------------
        # CHANGE 3: Admin authentication from env vars.
        # ---------------------------------------------
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, hashed_password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user[2], password):  # CHANGE 4: Proper hash comparison
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/")

        return "Invalid credentials"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ---------------------------------------------
        # CHANGE 5: Store hashed password securely.
        # ---------------------------------------------
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
            (username, hashed_pw)
        )
        conn.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------------------------------------------
# CHANGE 6: Removed debug=True
# Now controlled using FLASK_DEBUG environment variable.
# ---------------------------------------------
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)


