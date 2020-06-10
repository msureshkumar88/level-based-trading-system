from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from utilities.helper import Helper
from django.db import connection
from django.http import JsonResponse
import pandas as pd


def view(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    data = dict()
    if not ac.is_user_logged_in():
        return redirect('/login')
    cursor = connection.cursor()
    data["currency_pairs"] = cursor.execute("SELECT * FROM currency_pairs")
    data['auth'] = ac.is_user_logged_in()
    return render(request, 'insights.html', data)


def get_forecast(request):
    post = request.POST
    currency_pair = post["currency_pair"]
    data = dict()
    cursor = connection.cursor()
    today_date = Helper.get_today_date()
    result = cursor.execute(f"SELECT * FROM forecast WHERE currency_pair = '{currency_pair}' AND "
                            f"date < '{today_date}'")
    result = result.all()
    if result:
        df = pd.DataFrame(result)
        data["date"] = df['date'].astype(str).to_json(orient='records')
        data["value"] = df['value'].astype(float).to_json(orient='records')
        return JsonResponse(Helper.get_json_response(True, data, []))
    return JsonResponse(Helper.get_json_response(False, {}, []))
