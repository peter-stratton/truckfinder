# -*- coding: utf-8 -*-

__author__ = 'Peter Stratton'
__email__ = 'stratton.peter@gmail.com'
__version__ = '0.0.1'

from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    DEBUG = False
    PORT = 5000
    DB_NAME = 'truckfinder'
    DB_USER = 'truckfinder'
    DB_PASS = 'truckfinder'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
