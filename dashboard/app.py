from flask import Flask, render_template

from sysdata.data_blob import dataBlob

from sysproduction.data.prices import diagPrices
from sysproduction.reporting import roll_report
from sysproduction.data.broker import dataBroker
from sysproduction.data.capital import dataCapital
from sysproduction.data.positions import diagPositions, dataOptimalPositions

from syscore.objects import missing_order
from syscore.dateutils import get_datetime_input
from syscore.interactive import get_and_convert, run_interactive_menu, print_menu_of_values_and_get_response
from syscore.pdutils import set_pd_print_options

from sysdata.data_blob import dataBlob
from sysproduction.data.positions import diagPositions, dataOptimalPositions
from sysproduction.data.broker import dataBroker
from sysproduction.data.strategies import get_valid_strategy_name_from_user
from sysproduction.data.contracts import (
    get_valid_instrument_code_and_contractid_from_user,
)
from sysproduction.data.controls import dataLocks
from sysproduction.data.prices import get_valid_instrument_code_from_user

from sysexecution.stack_handler.stack_handler import stackHandler
from sysexecution.stack_handler.balance_trades import stackHandlerCreateBalanceTrades
from sysexecution.stack_handler.spawn_children_from_instrument_orders import map_instrument_order_type_to_contract_order_type
from sysexecution.orders.broker_orders import brokerOrder, balance_order_type as broker_balance_order_type
from sysexecution.orders.contract_orders import contractOrder
from sysexecution.orders.instrument_orders import instrumentOrder, market_order_type, instrumentOrderType, balance_order_type as instrument_balance_order_type
from sysexecution.algos.allocate_algo_to_order import list_of_algos


from pprint import pprint

app = Flask(__name__)

data = dataBlob(log_name="dashboard")


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


@app.route("/strategy")
def strategy():
    diag_positions = diagPositions(data)
    data_optimal = dataOptimalPositions(data)
    data_broker = dataBroker(data)
    optimal_positions = data_optimal.get_pd_of_position_breaks().to_dict()
    strategies = {}
    for instrument in optimal_positions["breaks"].keys():
        strategies[instrument] = {
            "break": optimal_positions["breaks"][instrument],
            "optimal": str(optimal_positions["optimal"][instrument]),
            "current": optimal_positions["current"][instrument],
        }
    pprint(strategies)
    """
    ans2 = data_broker.get_db_contract_positions_with_IB_expiries().to_dict()
    pprint(ans2)
    ans3 = data_broker.get_all_current_contract_positions().to_dict()
    pprint(ans3)
    """
    breaks = diag_positions.get_list_of_breaks_between_contract_and_strategy_positions()
    # breaks = data_broker.get_list_of_breaks_between_broker_and_db_contract_positions()
    return {"overall": "green", "strategy": strategies}


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
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)
