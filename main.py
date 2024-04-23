from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection(conn):
    conn.close()


def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL)')
    conn.close()


@app.route('/')
def index():
    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title, content) VALUES ("Why I love Flask", "This is so cool!!!")')
    conn.execute('INSERT INTO posts (title, content) VALUES ("Cats >> Dogs", "It was a joke because they are all so adorable.")')
    conn.execute('INSERT INTO posts (title, content) VALUES ("Hello Hello", "asdfasdfs")')
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


@app.route("/<int:post_id>/delete/", methods=('POST',))
def post_del(post_id):
    # post = get_post(post_id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    # flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # проверка логина и пароля
        return 'Вы вошли в систему!'
    else:
        return render_template('login.html')

@app.before_first_request
def before_first_request():
    init_db()


if __name__ == '__main__':
    app.run()
