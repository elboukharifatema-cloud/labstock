import sqlite3
import os
import click
from flask import g, current_app


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    base_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base_dir, 'schema.sql'), 'r', encoding='utf-8') as f:
        db.executescript(f.read())

    seed_path = os.path.join(base_dir, 'seed.sql')
    if os.path.exists(seed_path):
        with open(seed_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())

    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)

    @app.cli.command('init-db')
    def init_db_command():
        """Initialise la base de données."""
        os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
        init_db()
        click.echo('Base de données initialisée.')
