## Getting Started

### Clone the repository

git clone https://github.com/Ashokkoirala10/Blog-Application.git
cd flask_simple_blog


### Set up Python environment

python -m venv blog_env
# Activate the environment:
# Windows
blog_env\Scripts\activate
# Linux / Mac
source blog_env/bin/activate


### Install dependencies

pip install -r requirements.txt


###  Run the application

python app.py


## Access the app
Open your browser and go to http://127.0.0.1:5000
.

⚠️ Note: No database setup or migrations are required. The app uses SQLite (blog.db) and automatically creates the tables on first run.

## Features

User registration, login, and logout

Create, read, update, delete blog posts

View all posts on the home page

Dashboard for managing your own posts

Pagination for multiple posts

Clean and responsive layout with minimal styling

Secure password hashing using werkzeug.security

## Notes

Default database file: blog.db (SQLite)

Each post's Delete and Edit buttons are protected: only the author can perform these actions

Modify POSTS_PER_PAGE in app.py to change pagination size

