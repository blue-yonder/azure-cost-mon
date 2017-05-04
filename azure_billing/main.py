from os import getcwd
from flask import Flask, Response, abort
from .scrape import query_metrics


app = Flask(__name__)

#TODO proper testing should make it unnecessary to have that file
app.config.from_pyfile(getcwd()+"/application.cfg")


@app.route("/health")
def health():
    return 'ok'


@app.route("/metrics", methods=['GET'])
def metrics():

    try:
        metrics = query_metrics(app.config['ENROLLMENT_NUMBER'],
                                app.config['BILLING_API_ACCESS_KEY'],
                                app.config.get('PROMETHEUS_METRIC_NAME', 'azure_costs')
                                )
    except Exception as e:
        abort(Response("Scrape failed: {}".format(e),
                       status=502)
              )

    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
