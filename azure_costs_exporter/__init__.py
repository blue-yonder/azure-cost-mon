from .main import create_app
from os import path, getcwd

app = create_app(path.join(getcwd(), 'application.cfg'))
