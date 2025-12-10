# Simple Blog Application

This is a simple blog web application built with **Flask** and **SQLAlchemy**.  
It supports user registration, login/logout, creating, editing, deleting posts, and pagination.

---

## Getting Started

1. Clone the repository
```bash
git clone https://github.com/Ashokkoirala10/Blog-Application.git
cd flask_simple_blog


2. Start your SQL server

Make sure MySQL/MariaDB is running.

3. Create the database

Login to MySQL and create the database:

CREATE DATABASE blogdb;

4. Set up Python environment
python -m venv blog
cd blog_simple_blog
source blog/Scripts/activate   # Windows
# OR

source blog/bin/activate       # Linux/Mac



5. Install dependencies
pip install -r requirements.txt



6. Update database URL (if needed)

Open app.py and edit the database URL at the top if needed:

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/blogdb"



7. Run the application
python app.py



The app will start on http://127.0.0.1:5000/.



##Features

User registration, login, and logout

Create, read, update, delete blog posts

View all posts on the home page

Pagination for multiple posts

Dashboard for managing your own posts

Simple responsive layout with basic styling


##Notes

Default user password is hashed with werkzeug.security.

Delete button is protected with author check.

Modify POSTS_PER_PAGE in app.py to change pagination size.