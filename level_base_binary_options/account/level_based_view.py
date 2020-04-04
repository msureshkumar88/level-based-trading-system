from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime
from datetime import timedelta

from utilities.helper import Helper
from .models import UserTransactionsBinary
from .models import TransactionsByStatusBinary
from utilities.trading import Trading


def levels(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    data = dict()
    data = Trading.load_static_data()
    if request.method == "POST":
        create_trade(request)

    return render(request, 'level_based.html', data)


def create_trade(req):
    post = req.POST
    currency = post['currency']
    time_to_close = post['time_to_close']
    time_slot = post['time_slot']
    time_count = post['time_count']
    end_date = post['end_date']
    end_time = post['end_time']
    amount = post['amount']
    purchase = post['purchase']
    gap_pips = post['gap_pips']
    select_level = post['select_level']
    trade_type = 'levels'

    price = Helper.get_current_price(currency)

    trade_start_time = datetime.now()
    error_messages = []
    error_messages.extend(validate_currency(currency))
    error_messages.extend(validate_pip_gaps(gap_pips))
    error_messages.extend(validate_levels(select_level))
    error_messages.extend(validate_time_to_close(time_to_close))
    error_messages.extend(validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time))
    error_messages.extend(validate_amount(amount))

    if error_messages:
        # print(error_messages)
        return error_messages


def validate_currency(currency):
    if not currency:
        return ['Please select a currency pair']
    return []


def validate_pip_gaps(gap):
    if not gap:
        return ['Please select a level gap to generate levels']
    if int(gap) < 1:
        return ['The gap should be greater than 0 ']
    return []


def validate_levels(level):
    if not level:
        return ['Please select a preferred level']
    level = int(level)
    if level < 1 or level > 4:
        return ['Please select a valid level']
    return []


def validate_time_to_close(time_to_close):
    if not time_to_close:
        return ['Please select a closing type']
    return []


def validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time):
    if time_to_close == "Duration":
        if not time_slot:
            return ['Please select a type of duration']
        if not time_count:
            return ['Please enter end duration']
        if not time_slot and not time_count:
            return ['Please fill both type of end time and duration units']
    if time_to_close == "End Time":
        if not end_date:
            return ['Please fill trade end date']
        if not end_time:
            return ['Please fill trade end time']
        if not end_date and not end_time:
            return ['Please fill both trade end date and time']
    return []


def validate_amount(amount):
    if not amount:
        return ['Please enter amount']
    if float(amount) < 1:
        return ['Amount should be greater than 0']
    return []
