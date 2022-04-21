import sqlite3

import click
from flask import current_app
from flask import Flask
from flask import g
from flask.cli import with_appcontext


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """Register close_db and init_db_command functions with the application."""
    app.teardown_appcontext(close_db)  # call when cleaning up after reponse
    app.cli.add_command(init_db_command)  # can now be called with `flask` cmd
