import click
from hostelHub import app, db
from hostelHub.models.user_models import User, Role,user_datastore




@app.cli.command("create-admin")
def create_admin():
    username = click.prompt("Enter the admin's username",type =str)
    email = click.prompt("Enter the admin's email address",type=str)
    password = click.prompt("Enter the admin's password",type=str)

    admin =User(username=username,email=email,password=password)
    user_datastore.add_role_to_user(user=admin,role="admin")
    db.session.add(admin)
    db.session.commit()
    click.echo('You have succesfully created an admin')


@app.cli.command("create-role")
@click.argument("name")
def create_role(name):
    role = Role(name=name)
    click.echo(f"Succesfully created role {name}")
   
    db.session.add(role)
    db.session.commit()
