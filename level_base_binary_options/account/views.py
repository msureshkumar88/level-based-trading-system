from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime


# Create your views here.


def account(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = load_static_data();
    if request.method == "POST":
        data["errors"] = create_trade(request)

    return render(request, 'account.html', data)


def create_trade(req):
    post = req.POST
    start = post['start']
    start_date = post['start_date']
    start_time = post['start_time']
    currency = post['currency']
    time_to_close = post['time_to_close']
    time_slot = post['time_slot']
    end_date = post['end_date']
    end_time = post['end_time']
    amount = post['amount']

    error_messages = []

    trade_start_time = ""

    trade_start_time = get_trade_start_time(start, start_date, start_time)
    if not trade_start_time:
        error_messages.append("Invalid start date and time")

    if error_messages:
        return error_messages
    print(trade_start_time)


def get_trade_start_time(start, date, time):
    if start == "start now":
        return datetime.now()
    if validate_start_end_time(make_date_time_stamp(date, time)):
        return make_date_time_stamp(date, time)
    return ""


def load_static_data():
    cursor = connection.cursor()
    currencies = cursor.execute("SELECT * FROM currency")
    duration = cursor.execute("SELECT * FROM duration")

    data = dict()
    data['currency'] = currencies
    data['duration'] = duration
    data['today_date'] = datetime.now().strftime("%Y-%m-%d")
    data['time_now'] = datetime.now().strftime("%H:%M")
    return data


def validate_start_end_time(date_time):
    if datetime.now() >= date_time:
        return False
    return True


def make_date_time_stamp(date, time):
    return datetime.strptime(date + " " + time + ":00", '%Y-%m-%d %H:%M:%S')
