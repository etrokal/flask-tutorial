import sqlite3
from datetime import datetime
import click
from flask import Flask, current_app, g

from collections.abc import Callable


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            database=current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    db: sqlite3.Connection = g.pop('db', None)

    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command() -> None:
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    'timestamp', lambda v: datetime.fromisoformat(v.decode()))


def init_app(app: Flask):
    app.teardown_appcontext(f=close_db)
    app.cli.add_command(cmd=init_db_command, name='init-db')
