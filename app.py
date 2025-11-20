from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

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
            "image": "https://images.unsplash.com/photo-1574158622682-e40e69881006?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        }
    ]

    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now(),
        cats=featured_cats # Passing the list to the HTML
    )