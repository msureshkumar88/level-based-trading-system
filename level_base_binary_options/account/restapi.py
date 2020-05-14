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
    print(trade)

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
    else:
        trade_data['amount'] = trade['amount']
    trade_data['user_currency'] = current_user['currency']
    trade_data['staring_price'] = trade['staring_price']
    trade_data['closing_price'] = trade['closing_price']
    trade_data['outcome'] = trade['outcome']

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
        print(start_date, end_date)
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
