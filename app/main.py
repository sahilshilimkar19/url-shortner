from flask import Flask, render_template, request, redirect, flash, url_for
from app.db import init_db, get_db_connection
import string, random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

init_db()  # Create DB on startup

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        original_url = request.form["original_url"]
        short_code = generate_short_code()

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                (original_url, short_code)
            )
            conn.commit()
            flash(f"Short URL: http://127.0.0.1:5000/{short_code}")
        except Exception as e:
            flash("Error: Could not shorten the URL. Try again.")
        finally:
            conn.close()

    return render_template("index.html")

@app.route("/<short_code>")
def redirect_url(short_code):
    conn = get_db_connection()
    result = conn.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()
    conn.close()

    if result:
        return redirect(result["original_url"])
    else:
        return "URL not found", 404
