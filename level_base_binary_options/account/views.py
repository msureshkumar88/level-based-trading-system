from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime

from utilities.helper import Helper
from utilities.trading import Trading
from .models import UserTransactionsBinary
from .models import TransactionsByStatusBinary
from .models import UserTransactionsIdBinary
from cassandra.util import datetime_from_timestamp
from utilities.trade_status import Status


# Create your views here.


def account(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = Trading.load_static_data()
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
    trade_type = 'binary'
    price = Helper.get_current_price(currency)

    error_messages = []

    trade_start_time = ""

    ac = Authentication(req)
    user_id = ac.get_user_session()

    # error_messages.extend(Trading.validate_start_date(start,start_date, start_time))
    # error_messages.extend(Trading.validate_currency(currency))
    # error_messages.extend(Trading.validate_time_to_close(time_to_close))
    # error_messages.extend(Trading.validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time))
    # error_messages.extend(Trading.validate_amount(amount, user_id))
    trade_start_time = Trading.get_trade_start_time(start, start_date, start_time)
    trade_end_time = Trading.get_trade_end_time(time_to_close, end_date, end_time, time_slot, time_count, start,
                                                trade_start_time)

    error_messages.extend(Trading.validate_def_start_end_dates(trade_start_time, trade_end_time))
    
    purchase_type = Trading.get_trade_type(purchase)
    status = Trading.get_trade_status(start)

    print(error_messages)
    if error_messages:
        return error_messages
    # create new binary trade here

    time_now = Helper.get_current_time_formatted()
    date_time_now = datetime.now()
    use_trade = UserTransactionsIdBinary(user_id=user_id, created_date=date_time_now)

    use_trade.save()

    # new_d = time_now.strftime("%Y-%m-%d %H:%M:%S.%f%z")
    # print(new_d)
    # return
    cursor = connection.cursor()
    q = f"SELECT * FROM user_transactions_id_binary WHERE user_id = {user_id} and created_date = '{time_now}'"
    # print(q)

    transaction_id = cursor.execute(q)
    transaction_id = transaction_id[0]["id"]

    trade = UserTransactionsBinary(id=transaction_id, user_id=user_id, created_date=date_time_now,
                                   trade_type=trade_type, purchase_type=purchase_type,
                                   currency=currency, staring_price=price, amount=float(amount),
                                   start_time=trade_start_time, end_time=trade_end_time, status=status)
    trade.save()
    trades_by_status = TransactionsByStatusBinary(id=transaction_id, user_id=user_id, created_date=date_time_now,
                                                  trade_type=trade_type, purchase_type=purchase_type,
                                                  currency=currency, staring_price=price, amount=float(amount),
                                                  start_time=trade_start_time, end_time=trade_end_time, status=status)

    trades_by_status.save()


def search(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'level_trade_search.html', data)


def statements(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'statements.html', data)


def settings(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'settings.html', data)


def charts(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'charts.html', data)


