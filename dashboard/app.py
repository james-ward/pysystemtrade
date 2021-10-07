from flask import Flask, render_template, _app_ctx_stack
from werkzeug.local import LocalProxy

from sysdata.data_blob import dataBlob

from sysproduction.data.prices import diagPrices
from sysproduction.reporting import roll_report
from sysproduction.data.broker import dataBroker
from sysproduction.data.capital import dataCapital
from sysproduction.data.positions import diagPositions, dataOptimalPositions

from pprint import pprint

app = Flask(__name__)


def get_data():
    top = _app_ctx_stack.top
    if not hasattr(top, "data"):
        top.data = dataBlob(log_name="dashboard")
    return top.data


data = LocalProxy(get_data)


def get_data_broker():
    top = _app_ctx_stack.top
    if not hasattr(top, "data_broker"):
        top.data_broker = dataBroker(get_data())
    return top.data_broker


data_broker = LocalProxy(get_data_broker)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/capital")
def capital():
    capital_data = dataCapital(data)
    capital_series = capital_data.get_series_of_all_global_capital()
    now = capital_series.iloc[-1]["Actual"]
    yesterday = capital_series.last("1D").iloc[0]["Actual"]
    return {"now": now, "yesterday": yesterday}


@app.route("/reconcile")
def reconcile():
    diag_positions = diagPositions(data)
    data_optimal = dataOptimalPositions(data)
    optimal_positions = data_optimal.get_pd_of_position_breaks().to_dict()
    strategies = {}
    for instrument in optimal_positions["breaks"].keys():
        strategies[instrument] = {
            "break": optimal_positions["breaks"][instrument],
            "optimal": str(optimal_positions["optimal"][instrument]),
            "current": optimal_positions["current"][instrument],
        }

    db_contract_pos = (
        data_broker.get_db_contract_positions_with_IB_expiries().as_pd_df().to_dict()
    )
    positions = {}
    for idx in db_contract_pos["instrument_code"].keys():
        code = db_contract_pos["instrument_code"][idx]
        contract_date = db_contract_pos["contract_date"][idx]
        position = db_contract_pos["position"][idx]
        positions[code + "-" + contract_date] = {
            "code": code,
            "contract_date": contract_date,
            "db_position": position,
        }
    ib_contract_pos = (
        data_broker.get_all_current_contract_positions().as_pd_df().to_dict()
    )
    for idx in ib_contract_pos["instrument_code"].keys():
        code = ib_contract_pos["instrument_code"][idx]
        contract_date = ib_contract_pos["contract_date"][idx]
        position = ib_contract_pos["position"][idx]
        positions[code + "-" + contract_date]["ib_position"] = position

    db_breaks = (
        diag_positions.get_list_of_breaks_between_contract_and_strategy_positions()
    )
    ib_breaks = (
        data_broker.get_list_of_breaks_between_broker_and_db_contract_positions()
    )
    return {
        "strategy": strategies,
        "positions": positions,
        "db_breaks": db_breaks,
        "ib_breaks": ib_breaks,
    }


@app.route("/traffic_lights")
def traffic_lights():
    traffic_lights = {
        "stack": "green",
        "gateway": "red",
        "prices": "orange",
        # "capital": 123456,
        "breaks": "green",
    }
    return traffic_lights


@app.route("/rolls")
def rolls():
    # If we have a dictionary, Flask will automatically json-ify it
    diag_prices = diagPrices(data)

    all_instruments = diag_prices.get_list_of_instruments_in_multiple_prices()
    report = {}
    for instrument in all_instruments:
        report[instrument] = roll_report.get_roll_data_for_instrument(instrument, data)
    return report


if __name__ == "__main__":
    # strategy()
    app.run(
        threaded=False, use_debugger=False, use_reloader=False, passthrough_errors=True
    )
