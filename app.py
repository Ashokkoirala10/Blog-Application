import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from models import User, Post

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

# --- SQLite DB ---
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

POSTS_PER_PAGE = 6

with app.app_context():
    db.create_all()


# ----------------------
# Helper: get logged-in user
# ----------------------
def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    # Updated for SQLAlchemy 2.x
    return db.session.get(User, uid)


# ----------------------
# ROOT ROUTE → redirect to login
# ----------------------
@app.route('/')
def root():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


# ----------------------
# LOGIN
# ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials")
            return redirect(url_for('login'))

        session['user_id'] = user.id
        flash(f"Welcome, {user.username}!")
        return redirect(url_for('home'))

    return render_template("login.html")


# ----------------------
# REGISTER
# ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields required")
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash("Username already taken")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully. Please login.")
        return redirect(url_for('login'))

    return render_template("register.html")


# ----------------------
# LOGOUT
# ----------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out")
    return redirect(url_for('login'))


# ----------------------
# HOME → All posts
# ----------------------
@app.route('/home')
def home():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=POSTS_PER_PAGE
    )

    return render_template('home.html', posts=posts, user=user)


# ----------------------
# MY POSTS → Dashboard
# ----------------------
@app.route('/myposts')
def my_posts():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author_id=user.id).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=POSTS_PER_PAGE)

    return render_template('myposts.html', posts=posts, user=user)


# ----------------------
# CREATE POST
# ----------------------
@app.route('/create', methods=['GET', 'POST'])
def create():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        if not title or not body:
            flash("All fields required")
            return redirect(url_for('create'))

        post = Post(title=title, body=body, author_id=user.id)
        db.session.add(post)
        db.session.commit()

        flash("Post created")
        return redirect(url_for('my_posts'))

    return render_template('edit_post.html', action="Create", user=user)


# ----------------------
# EDIT POST
# ----------------------
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    if post.author_id != user.id:
        flash("Not allowed")
        return redirect(url_for('my_posts'))

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        db.session.commit()
        flash("Post updated")
        return redirect(url_for('my_posts'))

    return render_template('edit_post.html', post=post, action="Edit", user=user)


# ----------------------
# DELETE POST
# ----------------------
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    if post.author_id != user.id:
        flash("Not allowed")
        return redirect(url_for('my_posts'))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted")
    return redirect(url_for('my_posts'))


# ----------------------
# VIEW SINGLE POST
# ----------------------
@app.route('/post/<int:post_id>')
def view_post(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post, user=user)


# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
