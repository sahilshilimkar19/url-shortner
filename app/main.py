from flask import Flask, render_template, request, redirect, flash, url_for, session
from app.db import init_db, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use env variable in production

init_db()  # Creates tables on startup

# Utility: generate random short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Home Page – handles form & display
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        original_url = request.form["original_url"]
        custom_code = request.form.get("custom_code")
        user_id = session.get("user_id")

        short_code = custom_code if user_id and custom_code else generate_short_code()

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO urls (original_url, short_code, user_id) VALUES (?, ?, ?)",
                (original_url, short_code, user_id)
            )
            conn.commit()
            flash(f"Short URL: {request.host_url}{short_code}")
        except:
            flash("Short code already in use or error occurred.")
        finally:
            conn.close()

    return render_template("index.html")

# Redirect route
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

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            flash("Account created! Please log in.")
            return redirect(url_for("login"))
        except:
            flash("Username already exists.")
        finally:
            conn.close()

    return render_template("signup.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully.")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials.")

    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("home"))

# Dashboard to view user’s URLs
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login to access your dashboard.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    urls = conn.execute("SELECT * FROM urls WHERE user_id = ?", (session["user_id"],)).fetchall()
    conn.close()

    return render_template("dashboard.html", urls=urls)
