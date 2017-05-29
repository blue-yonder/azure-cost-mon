from os import getcwd
from flask import Flask
from prometheus_client import REGISTRY
from azure_costs_exporter.prometheus_collector import AzureEABillingCollector


def create_app():
    from azure_costs_exporter.views import bp

    app = Flask(__name__)
    app.config.from_pyfile(getcwd()+"/application.cfg")
    app.register_blueprint(bp)

    collector = AzureEABillingCollector(
                    app.config['PROMETHEUS_METRIC_NAME'],
                    app.config['ENROLLMENT_NUMBER'],
                    app.config['BILLING_API_ACCESS_KEY']
                )
    try:
        REGISTRY.register(collector)
    except ValueError:
        #don't register multiple times
        pass

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
