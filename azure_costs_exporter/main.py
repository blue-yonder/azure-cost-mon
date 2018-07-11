from os import getcwd, path
from flask import Flask


def create_app(configuration_path):
    from azure_costs_exporter.views import bp
    app = Flask(__name__)
    app.config.from_pyfile(configuration_path)
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    app = create_app(path.join(getcwd(), "application.cfg"))
    app.run(debug=True, host='0.0.0.0')
