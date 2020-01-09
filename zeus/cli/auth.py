import click
import zeus.auth

from zeus.models import User

from .base import cli


@cli.group("auth")
def auth():
    pass


@auth.command()
@click.argument("email", required=True)
def generate_token(email):
    user = User.query.filter(User.email == email).first()
    tenant = zeus.auth.Tenant.from_user(user)
    token = zeus.auth.generate_token(tenant)
    print('Authentication for "%s"' % user.email)
    print("User ID")
    print("  %s " % str(user.id))
    print("Email")
    print("  %s " % user.email)
    print("Token")
    print("  %s " % token.decode("utf-8"))
