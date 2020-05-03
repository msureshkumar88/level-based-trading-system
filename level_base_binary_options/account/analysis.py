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
        data = get_initial_chart_data(user_id)

    return JsonResponse(Helper.get_json_response(True, data, []))


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
