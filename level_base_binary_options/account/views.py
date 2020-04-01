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

    cursor = connection.cursor()
    currencies = cursor.execute("SELECT * FROM currency")
    duration = cursor.execute("SELECT * FROM duration")

    data = dict()
    data['currency'] = currencies
    data['duration'] = duration
    data['today_date'] = datetime.now().strftime("%Y-%m-%d")
    data['time_now'] = datetime.now().strftime("%H:%M")
    print(data)
    if request.method == "POST":
        create_trade(request)


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
    get_trade_start_time(start, start_date, start_time)


def get_trade_start_time(start, date, time):

    if start == "start now":
        return datetime.now()
    return datetime.strptime(date+ " " +time+":00", '%Y-%m-%d %H:%M:%S')
