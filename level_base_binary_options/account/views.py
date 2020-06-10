from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from django.http import JsonResponse

from django.db import connection
from datetime import datetime

from utilities.helper import Helper
from utilities.trading import Trading
from .models import UserTransactionsBinary
from .models import TransactionsByStatusBinary
from .models import UserTransactionsIdBinary

from .models import TransactionsByUser
from .models import UserTransactions
from .models import TransactionsByState
from .models import TransactionsByStartTime
from .models import TransactionsByEndTime
from .models import TransactionsChangesAllowedTime

from cassandra.util import datetime_from_timestamp
from utilities.trade_status import Status
from utilities.trade_type import Types
from utilities.trade_outcome import Outcome
from utilities.state_keys import StatKeys


# Create your views here.
def account(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = Trading.load_static_data()

    data['auth'] = ac.is_user_logged_in()
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
    error_messages = []

    trade_start_time = ""

    ac = Authentication(req)
    user_id = ac.get_user_session()

    error_messages.extend(Trading.validate_start_date(start, start_date, start_time))
    error_messages.extend(Trading.validate_currency(currency))
    error_messages.extend(Trading.validate_time_to_close(time_to_close))
    error_messages.extend(Trading.validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time))
    error_messages.extend(Trading.validate_amount(amount, user_id))
    trade_start_time = Trading.get_trade_start_time(start, start_date, start_time)
    trade_end_time = ""
    if trade_start_time:
        trade_end_time = Trading.get_trade_end_time(time_to_close, end_date, end_time, time_slot, time_count, start,
                                                    trade_start_time)

    if trade_start_time and trade_end_time:
        error_messages.extend(Trading.validate_def_start_end_dates(trade_start_time, trade_end_time))
        error_messages.extend(Trading.validate_close_time_day(trade_end_time))
        error_messages.extend(Trading.validate_start_time_day(trade_start_time))

    purchase_type = Trading.get_trade_type(purchase)
    status = Trading.get_trade_status(start)

    if error_messages:
        return JsonResponse(Helper.get_json_response(False, {}, error_messages))
    # create new binary trade here
    price = Helper.get_current_price(currency)
    time_now_formatted = Helper.get_current_time_formatted()
    time_now = datetime.strptime(time_now_formatted, '%Y-%m-%d %H:%M:%S.%f%z')
    changes_allowed_time = Trading.get_trade_changing_blocked_time(trade_start_time, trade_end_time)

    current_user = Helper.get_user_by_id(user_id)
    user_transaction = TransactionsByUser(user_id=user_id, created_date=time_now)

    user_transaction.save()
    cursor = connection.cursor()
    q = f"SELECT * FROM transactions_by_user WHERE user_id = {user_id} and created_date = '{time_now_formatted}'"

    transaction_id = cursor.execute(q)
    transaction_id = transaction_id[0]["id"]
    if start == "start now":
        user_transactions = f"insert into user_transactions (transaction_id, user_id,created_date," \
                            f"trade_type,purchase_type, currency,staring_price,amount,start_time,end_time," \
                            f"changes_allowed_time,outcome,status) values ({transaction_id},{user_id}," \
                            f"'{time_now_formatted}','{Types.BINARY.value}'," \
                            f"'{purchase_type}','{currency}',{float(price)},{float(amount)}," \
                            f"'{Helper.get_time_formatted(trade_start_time)}','{Helper.get_time_formatted(trade_end_time)}'," \
                            f"'{Helper.get_time_formatted(changes_allowed_time)}','{Outcome.NONE.value}','{status}')"
    else:
        user_transactions = f"insert into user_transactions (transaction_id, user_id,created_date," \
                            f"trade_type,purchase_type, currency,amount,start_time,end_time," \
                            f"changes_allowed_time,outcome,status) values ({transaction_id},{user_id}," \
                            f"'{time_now_formatted}','{Types.BINARY.value}'," \
                            f"'{purchase_type}','{currency}',{float(amount)}," \
                            f"'{Helper.get_time_formatted(trade_start_time)}','{Helper.get_time_formatted(trade_end_time)}'," \
                            f"'{Helper.get_time_formatted(changes_allowed_time)}','{Outcome.NONE.value}','{status}')"

    cursor.execute(user_transactions)

    state_transactions = TransactionsByState(transaction_id=transaction_id, user_id=user_id,
                                             purchase_type=purchase_type, currency=currency, outcome=Outcome.NONE.value,
                                             status=status, created_date=time_now, amount=float(amount),
                                             trade_type=Types.BINARY.value)
    state_transactions.save()

    transactions_by_start_time = f"INSERT INTO transactions_by_start_time (transaction_id,user_id,status,start_time) " \
                                 f"VALUES ({transaction_id},{user_id},'{status}'," \
                                 f"'{Helper.get_time_formatted(trade_start_time)}')"

    cursor.execute(transactions_by_start_time)
    transactions_by_end_time = f"INSERT INTO transactions_by_end_time (transaction_id,user_id,status,end_time," \
                               f"trade_type) VALUES ({transaction_id},{user_id},'{status}'," \
                               f"'{Helper.get_time_formatted(trade_end_time)}','{Types.BINARY.value}')"

    cursor.execute(transactions_by_end_time)

    transactions_changes_allowed_time = f"INSERT INTO transactions_changes_allowed_time " \
                                        f"(transaction_id,user_id,status,changes_allowed_time) " \
                                        f"VALUES ({transaction_id},{user_id},'{status}'," \
                                        f"'{Helper.get_time_formatted(changes_allowed_time)}')"

    cursor.execute(transactions_changes_allowed_time)

    # update account balance
    updated_amount = float(current_user['vcurrency']) - float(amount)
    user_vcurrency = f"UPDATE  user_by_id SET vcurrency = {updated_amount} WHERE id = {user_id}"
    cursor.execute(user_vcurrency)
    Helper.store_state_value(user_id, StatKeys.BALANCE.value, amount, 'subtract')
    Helper.store_state_value(user_id, StatKeys.NUM_TRADES.value, 1, 'add')
    Helper.store_state_value(user_id, StatKeys.BINARY.value, 1, 'add')
    Trading.save_purchase_stats(user_id, purchase_type)
    Trading.save_binary_general_stats(user_id, purchase_type)
    return JsonResponse(Helper.get_json_response(True, {'transaction_id': str(transaction_id), "user_id": str(user_id)},
                                                 ['Trade created successfully']))


def statements(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'statements.html', data)


def logout(request):
    ac = Authentication(request)
    if ac.is_user_logged_in():
        ac.logout()
    return redirect('/login')
