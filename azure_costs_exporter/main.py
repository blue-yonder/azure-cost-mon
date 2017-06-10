from os import getcwd
from flask import Flask


def create_app():
    from azure_costs_exporter.views import bp
    app = Flask(__name__)
    app.config.from_pyfile(getcwd()+"/application.cfg")
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
