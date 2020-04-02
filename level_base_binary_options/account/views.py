from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime
from datetime import timedelta

from utilities.helper import Helper
from .models import UserTransactionsBinary

from utilities.trade_status import Status


# Create your views here.


def account(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = load_static_data()
    if request.method == "POST":
        data["errors"] = create_trade(request)

    return render(request, 'account.html', data)


# start a trade
def create_trade(req):
    post = req.POST
    start = post['start']
    start_date = post['start_date']
    start_time = post['start_time']
    currency = post['currency']
    time_to_close = post['time_to_close']
    time_slot = post['time_slot']
    time_count = post['time_count']
    end_date = post['end_date']
    end_time = post['end_time']
    amount = post['amount']
    purchase = post['purchase']
    trade_type = 'Binary'
    price = Helper.get_current_price(currency)

    error_messages = []

    trade_start_time = ""

    trade_start_time = get_trade_start_time(start, start_date, start_time)
    if not trade_start_time:
        error_messages.append("Invalid start date and time")

    trade_end_time = get_trade_end_time(time_to_close, end_date, end_time, time_slot, time_count)
    if not trade_end_time:
        error_messages.append("Invalid end date and time")

    purchase_type = get_trade_type(purchase)
    status = get_trade_status(start)

    print(trade_end_time)
    if error_messages:
        return error_messages
    # create new binary trade here
    ac = Authentication(req)
    user_id = ac.get_user_session()
    trade = UserTransactionsBinary(user_id=user_id, created_date=datetime.now(),
                          trade_type=trade_type, purchase_type=purchase_type,
                          currency=currency, staring_price=price, amount=float(amount),
                          start_time=trade_start_time, end_time=trade_end_time, status=status)
    trade.save()


# generate trade start time
def get_trade_start_time(start, date, time):
    if start == "start now":
        return datetime.now()
    if validate_binary_trade_times(make_date_time_stamp(date, time)):
        return make_date_time_stamp(date, time)
    return ""


# generate trade end time
def get_trade_end_time(time_to_close, date, time, time_slot, time_count):
    if time_to_close == 'end_time':
        if validate_binary_trade_times(make_date_time_stamp(date, time)):
            return make_date_time_stamp(date, time)
        return ""
    time_count = int(time_count)
    if (time_slot == "seconds" and time_count < 5) or time_count < 1:
        return ""
    if time_slot == "seconds":
        return datetime.now() + timedelta(seconds=time_count)
    if time_slot == "minutes":
        return datetime.now() + timedelta(minutes=time_count)
    if time_slot == "hours":
        return datetime.now() + timedelta(hours=time_count)
    if time_slot == "days":
        return datetime.now() + timedelta(days=time_count)


# return static data for trade creation UI
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


# check whether selected dates are greater than current date and time
def validate_binary_trade_times(date_time):
    if datetime.now() >= date_time:
        return False
    return True


# convert date and time to system's format
def make_date_time_stamp(date, time):
    return datetime.strptime(date + " " + time + ":00", '%Y-%m-%d %H:%M:%S')


# get user selected trade type
def get_trade_type(purchase):
    if purchase == 'Buy':
        return 'buy'
    return 'sell'


# get the flag that determine trade start now or later
def get_trade_status(start):
    if start == "start now":
        return Status.STARTED.value
    return Status.PENDING.value
