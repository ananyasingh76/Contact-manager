from flask import Flask, request, redirect, render_template_string
import sqlite3
import re

app = Flask(__name__)

def get_db():
    return sqlite3.connect("contacts.db")

db = get_db()
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL
)
""")
db.commit()
db.close()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Contacts Manager</title>
    <style>
        body { font-family: Arial; margin: 30px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; }
        th { background-color: #f2f2f2; }
        input { padding: 6px; margin: 4px; }
        .error { color: red; }
    </style>
</head>
<body>

<h2>Contacts Manager</h2>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="post" action="/add">
    <input name="name" placeholder="Name" required>
    <input name="email" placeholder="Email" required>
    <input name="phone" placeholder="Phone" required>
    <button type="submit">Add</button>
</form>

<br>

<table>
<tr>
    <th>Name</th>
    <th>Email</th>
    <th>Phone</th>
    <th>Action</th>
</tr>
{% for c in contacts %}
<tr>
    <td>{{ c[1] }}</td>
    <td>{{ c[2] }}</td>
    <td>{{ c[3] }}</td>
    <td><a href="/delete/{{ c[0] }}">Delete</a></td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    db.close()
    return render_template_string(html, contacts=contacts)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return show_error("Invalid email format")

    if len(phone) < 10:
        return show_error("Phone must be at least 10 digits")

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone)
        )
        db.commit()
        db.close()
    except:
        return show_error("Email already exists")

    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/")

def show_error(message):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    db.close()
    return render_template_string(html, contacts=contacts, error=message)

if __name__ == "__main__":
    app.run(debug=True)
