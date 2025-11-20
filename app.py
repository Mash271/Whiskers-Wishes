import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the database using the variable from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended setting

db = SQLAlchemy(app)

# ... Your database models (classes) go here ...
# Model for the Cat data
class Cat(db.Model):
    # Primary Key
    id = db.Column(db.Integer, primary_key=True) 
    
    # Cat Information
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.String(50), nullable=False)
    story = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=True) # URL to the image

    # Optional: A helpful representation when debugging
    def __repr__(self):
        return f'<Cat {self.name} - {self.status}>'

# This route maps the root URL "/" to this function
@app.route("/")
@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name=None):
    # Data for the 3 featured cats (Requirement FR 2.1.1.1)
    featured_cats = [
        {
            "name": "Mochi",
            "age": "3 Months (Kitten)",
            "story": "Found in a cardboard box during a storm, Mochi is a tiny survivor with a huge heart. She loves chasing laser pointers and napping in shoes.",
            "status": "Available",
            "image": "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=400&q=80" 
        },
        {
            "name": "Luna",
            "age": "4 Years (Adult)",
            "story": "Luna is a calm, sophisticated lady who enjoys birdwatching from the window. She's looking for a quiet home where she can be the queen of the sofa.",
            "status": "Available",
            "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80"
        },
        {
            "name": "Oscar",
            "age": "12 Years (Senior)",
            "story": "Oscar is a wise soul who just wants a warm lap to sleep on. He purrs louder than a diesel engine and gives the best head-butts of affection.",
            "status": "Urgent Adoption",
            "image": "https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=400&q=80"}
    ]

    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now(),
        cats=featured_cats # Passing the list to the HTML
    )