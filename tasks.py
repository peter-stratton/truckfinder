import os

from invoke import task

HERE = os.path.dirname(__file__)
os.environ['FLASK_APP'] = os.path.join(HERE, 'truckfinder/autoapp.py')
os.environ['FLASK_DEBUG'] = '1'


# Database
@task
def db_init(ctx):
    ctx.run('flask db init')


@task
def db_migrate(ctx):
    ctx.run('flask db migrate')


@task
def db_upgrade(ctx):
    ctx.run('flask db upgrade')


@task
def db_downgrade(ctx):
    ctx.run('flask db downgrade')
