import os

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash,
    send_from_directory
    )
import sqlite3
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        )


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.execute('ATTACH DATABASE "database.db" AS main_db')

    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection(conn):
    conn.close()


def init_db():
    conn = get_db_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS posts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 title TEXT NOT NULL, 
                 content TEXT NOT NULL)""")
    conn.close()


@app.route('/')
def index():
    conn = get_db_connection()
    # conn.execute('INSERT INTO posts (title, content) VALUES ("Why I love Flask", "This is so cool!!!")')
    # conn.execute('INSERT INTO posts (title, content) VALUES ("Cats >> Dogs", "It was a joke because they are all so adorable.")')
    # conn.execute('INSERT INTO posts (title, content) VALUES ("Hello Hello", "asdfasdfs")')
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def get_post(post_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title, content) VALUES ("Random Title", "Lorem ipsum dolor sit amet consectetur adipiscing elit")')
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return render_template('post.html', post=post)


@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))
    return render_template('add_post.html')


@app.route('/<int:user_id>')
def get_user(user_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username) VALUES ("SuperUser")')
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return render_template('user_page.html', user=user)


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        # content = request.form['content']
        if not username:
            flash('username is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username) VALUES (?)',
                         (username,))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add_user.html')


@app.route('/upload', methods=('GET', 'POST'))
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('upload_file.html')

@app.route('/upload/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/<int:post_id>/edit', methods=('GET', 'POST'))
def edit(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # if not title:
        #     flash('Title is required!')
        # else:
        conn = get_db_connection()
        conn.execute('UPDATE posts SET title = ?, content = ?'
                    ' WHERE id = ?',
                    (title, content, post_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:post_id>/delete', methods=('POST',))
def post_del(post_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('Статья "{}" была удалена!')
    return redirect(url_for('index'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # проверка логина и пароля
#         return 'Вы вошли в систему!'
#     else:
#         return render_template('login.html')

@app.before_first_request
def before_first_request():
    init_db()


if __name__ == '__main__':
    app.run(debug=True)
