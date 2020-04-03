from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime
from datetime import timedelta

from utilities.helper import Helper
from .models import UserTransactionsBinary
from .models import TransactionsByStatusBinary


def levels(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    data = dict()
    if request.method == "POST":
        pass

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
    error_messages = []
    trade_start_time = datetime.now()
    
