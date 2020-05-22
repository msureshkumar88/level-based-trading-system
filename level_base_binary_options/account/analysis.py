from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from django.http import JsonResponse
from django.db import connection

from django.db import connection
from datetime import datetime
from datetime import timedelta
from datetime import date

from utilities.helper import Helper
from utilities.state_keys import StatKeys

import pandas as pd
import json


def chart_view(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass
    data['auth'] = ac.is_user_logged_in()
    return render(request, 'charts.html', data)


def chart(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return JsonResponse(Helper.get_json_response(False, [], ["Unauthorized Access"]))

    post = request.POST
    start_date = post['start_date']
    end_date = post['end_date']
    user_id = ac.get_user_session()
    data = []
    if not start_date and not end_date:
        return JsonResponse(Helper.get_json_response(True, get_initial_chart_data(user_id), []))
    stat_key = post['type']
    if stat_key == "buy_sell":
        return JsonResponse(
            get_chart_by_state_keys(user_id, [StatKeys.BUY.value, StatKeys.SELL.value], start_date, end_date))
    if stat_key == "win_loss_count":
        return JsonResponse(
            get_chart_by_state_keys(user_id, [StatKeys.WON.value, StatKeys.LOSS.value], start_date, end_date))

    return JsonResponse(get_filtered_chart_data(user_id, start_date, end_date, stat_key))


def get_initial_chart_data(user_id):
    cursor = connection.cursor()
    start = date.today() - timedelta(days=10)
    response = dict()
    for stst in StatKeys:
        print(stst.value)
        result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                f"AND type = '{stst.value}'and date >= '{start}'")
        if result:
            df = pd.DataFrame(result)

            item = dict()

            item['date'] = df['date'].astype(str).to_json(orient='records')
            item['value'] = df['value'].astype(float).to_json(orient='records')
            response[stst.value] = item
    return response


def get_chart_by_state_keys(user_id, key_list, start_date, end_date):
    cursor = connection.cursor()
    response = dict()
    result = []
    for stat_key in key_list:
        if not start_date:
            return Helper.get_json_response(False, dict(), ['Please select a start date'])
        if start_date and not end_date:
            result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                    f"AND type = '{stat_key}'and date >= '{start_date}'")
        if start_date and end_date:
            result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                    f"AND type = '{stat_key}'and date >= '{start_date}' "
                                    f"and date <= '{end_date}'")

        item = dict()
        item['date'] = json.dumps([])
        item['value'] = json.dumps([])
        response[stat_key] = item
        if result:
            df = pd.DataFrame(result)
            item['date'] = df['date'].astype(str).to_json(orient='records')
            item['value'] = df['value'].astype(float).to_json(orient='records')
            response[stat_key] = item
            # return Helper.get_json_response(True, response, [''])
        # return Helper.get_json_response(False, dict(), ['Data not available for this range'])
    return Helper.get_json_response(True, response, [])


def get_filtered_chart_data(user_id, start_date, end_date, stat_key):
    cursor = connection.cursor()

    result = []
    if not start_date:
        return Helper.get_json_response(False, dict(), ['Please select a start date'])
    if start_date and not end_date:
        result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                f"AND type = '{stat_key}'and date >= '{start_date}'")
    if start_date and end_date:
        result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                f"AND type = '{stat_key}'and date >= '{start_date}' "
                                f"and date <= '{end_date}'")

    if result:
        response = dict()
        df = pd.DataFrame(result)

        item = dict()

        item['date'] = df['date'].astype(str).to_json(orient='records')
        item['value'] = df['value'].astype(float).to_json(orient='records')
        response[stat_key] = item
        return Helper.get_json_response(True, response, [''])
    return Helper.get_json_response(False, dict(), ['Data not available for this range'])
