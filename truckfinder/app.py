# -*- coding: utf-8 -*-
"""Main App"""

from flask import Flask
from flask_migrate import Migrate

from truckfinder import Configuration
from truckfinder.models import db

# import models here so sqlalchemy will register them
import truckfinder.models.dealership
import truckfinder.models.price
import truckfinder.models.vehicle


def create_app():
    app = Flask(__name__)
    app.config.from_object(Configuration)

    db.init_app(app)
    migrate = Migrate(app, db)

    # Blueprints
    from truckfinder.views import frontend
    app.register_blueprint(frontend)

    return app


if __name__ == "__main__":
    create_app().run()
