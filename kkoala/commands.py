import click
from flask.cli import with_appcontext
from .models import User
from .extensions import db
from .utils import str_to_bool

@click.command('toggle-admin')
@click.argument('username')
@with_appcontext
def toggle_admin_command(username):
    """Toggle admin status for a user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'User {username} not found.')
        return

    user.is_admin = not user.is_admin
    db.session.commit()
    status = "Admin" if user.is_admin else "User"
    click.echo(f'User {username} is now {status}.')

@click.command('toggle-teacher')
@click.argument('username')
@with_appcontext
def toggle_teacher_command(username):
    """Toggle teacher status for a user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'User {username} not found.')
        return

    user.is_teacher = not user.is_teacher
    db.session.commit()
    status = "Teacher" if user.is_teacher else "User"
    click.echo(f'User {username} is now {status}.')

def register_commands(app):
    app.cli.add_command(toggle_admin_command)
    app.cli.add_command(toggle_teacher_command)
