# Lost & Found Web Application

#### Video Demo:  <https://youtu.be/GkL4-i4TEIQ>

#### Description:

**Lost & Found** is a robust web application designed to bridge the gap between individuals who have lost personal items and those who have found them.

The project is built using **Python and Flask** for the backend, **SQLite** for database management, and **Bootstrap 5** for a responsive frontend design.

### Key Features
* **User Authentication:** Secure registration and login system using password hashing (`werkzeug.security`) to protect user data. Session management ensures users can only modify their own posts.
* **Advanced Search & Filtering:** Users can filter items by Status (Lost/Found) and Category (Electronics, Pets, etc.), or use the **Keyword Search** bar to query titles and descriptions simultaneously.
* **Dashboard Management:** A dedicated "My Posts" area allows users to view their history, edit details, delete posts, or mark items as "Resolved" (Returned/Recovered).
* **Image Uploads:** Users can upload a photo of the item to assist in identification. Images are securely stored and referenced in the database.
* **Responsive Design:** The application is fully mobile-responsive, ensuring accessibility on phones, tablets, and desktops.

### File Structure & Design Decisions

The project is organized into a modular structure to ensure maintainability and scalability.

#### 1. Backend (`app.py`)
This is the core controller of the application.
* **Routes:** Defined for index, authentication, item CRUD operations (Create, Read, Update, Delete), and status updates.
* **Database Interaction:** Uses the CS50 SQL library to execute sanitized queries, preventing SQL injection attacks.

#### 2. Database (`schema.sql` & `lostfound.db`)
The database schema consists of two normalized tables:
* `users`: Stores user credentials (full name, email, password hash).
* `items`: Stores the details of the lost/found object (title, description, status, category, date), the `user_id` (Foreign Key), and the `image_path` for the uploaded photo.

#### 3. Templates (Frontend)
The HTML files use **Jinja2** templating engine to render dynamic data.
* `layout.html`: The base template containing the Navbar, Flash messaging system, and Bootstrap CDNs. All other pages extend this layout to ensure visual consistency.
* `index.html`: The landing page featuring card-based layouts for items and a search/filter form.
* `item_detail.html`: A detailed view page displaying the item's image and contact information side-by-side.
* `my_posts.html`: A dashboard table giving users administrative control over their specific submissions.
* `add_item.html` / `edit_item.html`: Forms for data entry, including logic to pre-fill data when editing.

#### 4. Static Assets (`static/`)
* `css/styles.css`: Custom CSS overrides to refine the Bootstrap look (e.g., hover effects on cards).
* `uploads/`: The directory where user-uploaded images are stored.

### How to Run
1.  Ensure Python and Flask are installed:
    ```bash
    pip install flask cs50 werkzeug
    ```
2.  Initialize the database:
    ```bash
    sqlite3 lostfound.db < schema.sql
    ```
3.  Start the application:
    ```bash
    python app.py
    or flask run
    ```
4.  Open a browser
