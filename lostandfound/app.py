import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection
db = SQL("sqlite:///lostfound.db")

# Configure Uploads
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Create directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----ROUTES


@app.route("/")
def index():
    # Get all filter params
    status = request.args.get("status")
    category = request.args.get("category")
    search_query = request.args.get("q")  # Get the search keyword

    #  base query
    sql_query = "SELECT * FROM items WHERE 1=1"
    params = []

    #  Filter by Status (Lost/Found)
    if status:
        sql_query += " AND status = ?"
        params.append(status)
    else:
        sql_query += " AND status IN ('Lost', 'Found')"

    #  Filter by Category
    if category:
        sql_query += " AND category = ?"
        params.append(category)

    # 3. Filter by Search Keyword
    if search_query:
        sql_query += " AND (title LIKE ? OR description LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")

    # Order by newest first
    sql_query += " ORDER BY date_posted DESC"

    # Execute the final query
    items = db.execute(sql_query, *params)

    return render_template("index.html", items=items)

#  AUTHENTICATION


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]

        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if rows:
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                   full_name, email, hashed_pw)

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.execute("SELECT * FROM users WHERE email = ?", email)

        if len(user) == 1 and check_password_hash(user[0]["password_hash"], password):
            session["user_id"] = user[0]["id"]
            session["full_name"] = user[0]["full_name"]
            flash(f"Welcome back, {user[0]['full_name']}!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

# ITEM MANAGEMENT


@app.route("/add", methods=["GET", "POST"])
def add_item():
    if "user_id" not in session:
        flash("Please login to add an item.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        status = request.form["status"]
        contact_info = request.form["contact_info"]

        image = request.files.get("image")
        image_path = "static/images/default.jpg"

        if image and image.filename:
            filename = f"{datetime.now().timestamp()}_{image.filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(filepath)
            image_path = f"uploads/{filename}"

        db.execute("""
            INSERT INTO items (title, description, category, status, contact_info, image_path, user_id, date_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, title, description, category, status, contact_info, image_path, session["user_id"], datetime.now())

        flash("Item posted successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add_item.html")


@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = db.execute(
        "SELECT items.*, users.full_name FROM items JOIN users ON items.user_id = users.id WHERE items.id = ?", item_id)
    if not item:
        return "Item not found", 404
    return render_template("item_detail.html", item=item[0])

#  MY POSTS


@app.route("/my_posts")
def my_posts():
    if "user_id" not in session:
        flash("Login required.", "warning")
        return redirect(url_for("login"))

    items = db.execute(
        "SELECT * FROM items WHERE user_id = ? ORDER BY date_posted DESC", session["user_id"])
    return render_template("my_posts.html", items=items)


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = db.execute("SELECT * FROM items WHERE id = ? AND user_id = ?",
                      item_id, session["user_id"])

    if item:
        db.execute("DELETE FROM items WHERE id = ?", item_id)
        flash("Post deleted successfully.", "success")
    else:
        flash("Unauthorized action.", "danger")

    return redirect(url_for("my_posts"))

# EDIT ITEM


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = db.execute("SELECT * FROM items WHERE id = ? AND user_id = ?",
                      item_id, session["user_id"])

    if not item:
        flash("You do not have permission to edit this item.", "danger")
        return redirect(url_for("index"))

    item = item[0]

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        contact_info = request.form["contact_info"]
        db.execute("""
            UPDATE items
            SET title = ?, description = ?, category = ?, contact_info = ?
            WHERE id = ?
        """, title, description, category, contact_info, item_id)

        flash("Item updated successfully!", "success")
        return redirect(url_for("my_posts"))

    return render_template("edit_item.html", item=item)


# MARK AS RESOLVED

@app.route("/resolve/<int:item_id>", methods=["POST"])
def resolve_item(item_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Check ownership
    item = db.execute("SELECT * FROM items WHERE id = ? AND user_id = ?",
                      item_id, session["user_id"])

    if item:
        current_status = item[0]["status"]
        new_status = "Resolved"

        if current_status == "Lost":
            new_status = "Recovered"
        elif current_status == "Found":
            new_status = "Returned"

        db.execute("UPDATE items SET status = ? WHERE id = ?", new_status, item_id)
        flash(f"Item marked as {new_status}!", "success")
    else:
        flash("Unauthorized action.", "danger")

    return redirect(url_for("my_posts"))
