from flask import Flask, render_template

from sysdata.data_blob import dataBlob

from sysproduction.data.prices import diagPrices
from sysproduction.reporting import roll_report


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/rolls")
def rolls():
    # If we have a dictionary, Flask will automatically json-ify it
    data = dataBlob(log_name="dashboard")
    diag_prices = diagPrices(data)
    return {
        "CORN": {
            "status": "No_roll",
            "roll_expiry": 10,
            "carry_expiry": 20,
            "price_expiry": 30,
            "contract_labels": ["fee", "fi", "fo"],
        },
        "MXP": {
            "status": "No_roll",
            "roll_expiry": 10,
            "carry_expiry": 20,
            "price_expiry": 30,
            "contract_labels": ["fee", "fi", "fo"],
        },
    }
    all_instruments = diag_prices.get_list_of_instruments_in_multiple_prices()
    report = {}
    for instrument in all_instruments:
        report[instrument] = roll_report.get_roll_data_for_instrument(instrument, data)
    return report


if __name__ == "__main__":
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)
