from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.db import connection
from datetime import datetime
from datetime import timedelta
import pandas as pd

from utilities.authentication import Authentication
from utilities.helper import Helper
from utilities.trading import Trading
from utilities.trade_type import Types
from utilities.trade_status import Status
from utilities.trade_outcome import Outcome


def get_transaction(request):
    ac = Authentication(request)
    # if user is not logged in response user not exist
    if not ac.is_user_logged_in():
        return JsonResponse(Helper.get_json_response(False, [], ['Please login']))
    post = request.POST

    trade = Trading.get_transaction_by_id(post['transaction_ref'], post['trade_owner'])
    if not trade:
        return JsonResponse(Helper.get_json_response(False, [], ["Trade not available"]))
    user_id = ac.get_user_session()
    # print(trade)

    current_user = Helper.get_user_by_id(user_id)
    trade_data = dict()
    trade_data['contract_type'] = trade['trade_type']
    trade_data['transaction_ref'] = trade['transaction_id']
    trade_data['purchase_type'] = trade['purchase_type']
    trade_data['start_time'] = trade['start_time']
    trade_data['end_time'] = trade['end_time']
    if trade['trade_type'] == Types.LEVELS.value:
        trade_data['amount'] = Helper.convert_currency(trade['amount'], trade['amount_currency'],
                                                       current_user['currency'])
        trade_data['selected_level'] = trade['level_selected']
        trade_data['user_count'] = 4 - len(trade['available_levels'])
        trade_data['available_levels'] = trade['available_levels']
    else:
        trade_data['amount'] = trade['amount']
    trade_data['user_currency'] = current_user['currency']
    trade_data['staring_price'] = trade['staring_price']
    trade_data['closing_price'] = trade['closing_price']
    trade_data['outcome'] = trade['outcome']
    trade_data['status'] = trade['status']

    return JsonResponse(Helper.get_json_response(True, [trade_data], []))


def get_chart_data(request):
    post = request.POST
    currency = post['chart_currency']
    timeframe = post['timeframe']
    price_type = post['price_type']
    chart_type = post['chart_type']

    return get_history(currency, timeframe, price_type, chart_type)


def get_history(currency, timeframe, price_type, chart_type):
    start_date = ""
    end_date = ""
    if timeframe == 'ticks':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(hours=3))
        end_date = Helper.get_time_formatted(datetime.now())
        # print(start_date, end_date)
        table = "forex_pip_data"

    if timeframe == 'minute':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=3))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data"

    if timeframe == 'five_min':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=3))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data_five_min"

    if timeframe == 'fifteen_min':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=4))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data_fifteen_min"

    if timeframe == 'thirty_min':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=10))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data_thirty_min"

    if timeframe == 'hour':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=15))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data_one_hour"

    if timeframe == 'four_hours':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=15))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data_four_hours"

    if timeframe == 'one_day':
        start_date = Helper.get_time_formatted(datetime.now() - timedelta(days=100))
        end_date = Helper.get_time_formatted(datetime.now())
        table = "forex_data_one_day"

    cursor = connection.cursor()
    result = cursor.execute(f"SELECT * FROM {table} WHERE currency_pair = '{currency}' "
                            f"and timestamp > '{start_date}' AND timestamp < '{end_date}'")

    if not result:
        return JsonResponse(Helper.get_json_response(False, {}, ["Data Not available"]))

    df = pd.DataFrame(result)
    df = df.sort_values(by='timestamp', ascending=True)
    timestamp = df['timestamp'].astype(str).to_json(orient='records')
    data = dict()
    if chart_type == "line":
        if price_type == "close":
            close = df['close'].to_json(orient='records')

            data["timestamp"] = timestamp
            data["close"] = close

        if price_type == "open":
            open_price = df['open'].to_json(orient='records')

            data["timestamp"] = timestamp
            data["open"] = open_price

        if price_type == "high":
            high = df['high'].to_json(orient='records')

            data["timestamp"] = timestamp
            data["high"] = high

        if price_type == "low":
            low = df['low'].to_json(orient='records')
            data["timestamp"] = timestamp
            data["low"] = low

    if chart_type == "candlestick":
        close = df['close'].to_json(orient='records')
        open_price = df['open'].to_json(orient='records')
        high = df['high'].to_json(orient='records')
        low = df['low'].to_json(orient='records')

        data["timestamp"] = timestamp
        data["close"] = close
        data["open"] = open_price
        data["high"] = high
        data["low"] = low

    return JsonResponse(Helper.get_json_response(True, data, []))


def get_pending_order(request):
    post = request.POST
    transaction_id = post['transaction_id']
    user_id = post['user_id']
    result = Trading.get_transaction_by_id(transaction_id, user_id)
    if not result:
        return JsonResponse(Helper.get_json_response(False, {}, ["Trade data is not available"]))
    user_data = Helper.get_user_by_id(user_id)

    data = dict()
    data["transaction_id"] = result["transaction_id"]
    data["created_date"] = result["created_date"]
    data["trade_type"] = result["trade_type"].capitalize()
    data["purchase_type"] = result["purchase_type"].capitalize()
    data["currency"] = result["currency"]
    data["amount"] = result["amount"]
    data["start_time"] = str(result["start_time"])
    data["end_time"] = str(result["end_time"])
    data["changes_allowed_time"] = str(result["changes_allowed_time"])
    data["outcome"] = result["outcome"].capitalize()
    data["status"] = result["status"].capitalize()
    data["amount_currency"] = user_data["currency"]

    return JsonResponse(Helper.get_json_response(True, data, []))


# TODO: repay when close trade manually
def close_order(request):
    ac = Authentication(request)
    # if user is not logged in response user not exist
    if not ac.is_user_logged_in():
        return JsonResponse(Helper.get_json_response(False, [], ['Please login']))

    user_id = ac.get_user_session()

    post = request.POST
    transaction_id = post['transaction_id']

    transaction = Trading.get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        return JsonResponse(Helper.get_json_response(False, {}, ["Trade data is not available"]))

    if Trading.validate_changes_allowed_time_exceeded(transaction['changes_allowed_time']):
        return JsonResponse(Helper.get_json_response(False, {}, ["Trade closing time is expired and cannot be closed"]))

    update_transactions_by_state_outcome(transaction, Status.FINISHED.value, Outcome.NONE.value)
    Trading.pay_back(user_id, transaction['amount'])
    return JsonResponse(Helper.get_json_response(True, {}, ['Trade has been closed successfully']))


# only binary options trade manual trade close allowed
# the function only support binary options
def update_transactions_by_state_outcome(transaction, status, outcome):
    trade = transaction

    cursor = connection.cursor()

    closing_price = Helper.get_current_price(trade["currency"])

    query_update = ""

    query_update = query_update + f"UPDATE user_transactions " \
                                  f"SET status = '{status}', outcome ='{outcome}', " \
                                  f"closing_price = {closing_price} WHERE user_id = {transaction['user_id']} " \
                                  f"AND transaction_id = {transaction['transaction_id']}"
    cursor.execute("BEGIN BATCH " + query_update + "APPLY BATCH")

    delete_query = ""

    delete_query = delete_query + f"DELETE FROM transactions_by_state " \
                                  f"WHERE user_id = {transaction['user_id']} AND status = '{transaction['status']}' " \
                                  f"AND outcome = '{trade['outcome']}' " \
                                  f"AND created_date = '{Helper.remove_milliseconds(trade['created_date'])}'"

    delete_query = delete_query + f" DELETE FROM transactions_by_start_time " \
                                  f"WHERE status = '{transaction['status']}' " \
                                  f"AND start_time = '{Helper.remove_milliseconds(trade['start_time'])}' " \
                                  f"AND transaction_id = {transaction['transaction_id']} " \
                                  f"AND user_id = {transaction['user_id']}"

    delete_query = delete_query + f" DELETE FROM transactions_by_end_time " \
                                  f"WHERE status = '{transaction['status']}' " \
                                  f"AND end_time = '{Helper.remove_milliseconds(transaction['end_time'])}' " \
                                  f"AND transaction_id = {transaction['transaction_id']} " \
                                  f"AND user_id = {transaction['user_id']}"

    delete_query = delete_query + f" DELETE FROM transactions_changes_allowed_time " \
                                  f"WHERE status = '{transaction['status']}' " \
                                  f"AND changes_allowed_time = '{Helper.remove_milliseconds(trade['changes_allowed_time'])}' " \
                                  f"AND transaction_id = {transaction['transaction_id']} " \
                                  f"AND user_id = {transaction['user_id']}"
    # print(delete_query)
    cursor.execute("BEGIN BATCH " + delete_query + "APPLY BATCH")

    insert_query = ""

    transaction_id = trade['transaction_id']
    user_id = trade['user_id']
    currency = trade['currency']
    purchase_type = trade['purchase_type']
    created_date = Helper.remove_milliseconds(trade['created_date'])
    amount = trade['amount']
    trade_type = trade['trade_type']
    start_time = Helper.remove_milliseconds(trade['start_time'])
    end_time = Helper.remove_milliseconds(trade['end_time'])
    changes_allowed_time = Helper.remove_milliseconds(trade['changes_allowed_time'])

    insert_query = insert_query + f"INSERT INTO transactions_by_state " \
                                  f"(transaction_id, user_id, currency, purchase_type, outcome, status, " \
                                  f"created_date, amount, trade_type) " \
                                  f"VALUES " \
                                  f"({transaction_id}, {user_id},'{currency}','{purchase_type}','{outcome}'," \
                                  f"'{status}','{created_date}',{amount},'{trade_type}')"

    insert_query = insert_query + f"INSERT INTO transactions_by_start_time " \
                                  f"(transaction_id,user_id,status,start_time) " \
                                  f"VALUES " \
                                  f"({transaction_id},{user_id},'{status}','{start_time}')"

    insert_query = insert_query + f"INSERT INTO transactions_by_end_time " \
                                  f"(transaction_id,user_id,status,trade_type,end_time) " \
                                  f"VALUES " \
                                  f"({transaction_id},{user_id},'{status}'," \
                                  f"'{trade_type}','{end_time}')"

    insert_query = insert_query + f"INSERT INTO transactions_changes_allowed_time " \
                                  f"(transaction_id,user_id,status,changes_allowed_time) " \
                                  f"VALUES " \
                                  f"({transaction_id},{user_id},'{status}','{changes_allowed_time}')"

    cursor.execute("BEGIN BATCH " + insert_query + "APPLY BATCH")
