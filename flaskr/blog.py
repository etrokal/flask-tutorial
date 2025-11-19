

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username' +
        ' FROM post p JOIN user u ON p.author_id = u.id' +
        ' ORDER BY created DESC;'
    ).fetchall()
    return render_template('blog/index.jinja', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        elif not body:
            error = "Body is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)' +
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.jinja')

@bp.route('/update/<id>', methods=('GET', 'POST'))
@login_required
def update(id):
    db = get_db()
    user = g.user

    post = db.execute(
        'SELECT * FROM post WHERE id = ?',
        (id)
    ).fetchone()

    if not post:
        abort(404)

    if post['author_id'] != user['id']:
        abort(403)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."

        if not error:
            db.execute(
                'UPDATE post SET title=?, body=? WHERE id=?',
                (title, body, id)
            )
            db.commit()
            flash("Post updated successfully.")
            return redirect(url_for("index"))
        else:
            flash(error)

    return render_template("blog/update.jinja", title=post['title'], body=post['body'])

