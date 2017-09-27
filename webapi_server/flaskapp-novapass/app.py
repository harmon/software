from flask import Flask
from config import ConfigClass

app = None


def get_app():
    global app
    if app is None:
        app = Flask(__name__)
        app.config.from_object(ConfigClass)

    return app
