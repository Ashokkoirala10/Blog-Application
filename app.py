import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from models import User, Post
# from dotenv import load_dotenv

# load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

# Use MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/blogdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)



POSTS_PER_PAGE = 6

with app.app_context():
    db.create_all()



# Helper: current_user
def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)

# Home: list posts with pagination
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=POSTS_PER_PAGE)
    return render_template('index.html', posts=posts)


# Single post view
@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Dashboard
@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        flash('Please login first')
        return redirect(url_for('login'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).paginate(page=page, per_page=POSTS_PER_PAGE)
    return render_template('dashboard.html', posts=posts, user=user)

# Create post
@app.route('/create', methods=['GET', 'POST'])
def create():
    user = get_current_user()
    if not user:
        flash('Please login first')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        if not title or not body:
            flash('Title and body required')
            return redirect(url_for('create'))
        post = Post(title=title, body=body, author_id=user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post created')
        return redirect(url_for('dashboard'))
    return render_template('edit_post.html', action='Create')

# Edit post
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    user = get_current_user()
    if not user:
        flash('Please login first')
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    if post.author_id != user.id:
        flash('Not allowed')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        db.session.commit()
        flash('Post updated')
        return redirect(url_for('dashboard'))
    return render_template('edit_post.html', post=post, action='Edit')


# Delete post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    if post.author_id != user.id:
        flash('Not allowed')
        return redirect(url_for('dashboard'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted')
    return redirect(url_for('dashboard'))



# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')



# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid credentials')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        flash('Logged in')
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out')
    return redirect(url_for('index'))



@app.route('/api/posts')
def api_posts():
    page = request.args.get('page', 1, type=int)
    pag = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=POSTS_PER_PAGE)
    data = {
    'items': [p.to_dict() for p in pag.items],
    'page': pag.page,
    'pages': pag.pages,
    'total': pag.total,
    }
    return jsonify(data)

# REST API: single post
@app.route('/api/posts/<int:post_id>')
def api_get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


if __name__ == '__main__':
    app.run(debug=True)