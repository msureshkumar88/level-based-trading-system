from django.shortcuts import render, redirect
from utilities.authentication import Authentication

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
    if request.method == "POST":
        data["errors"] = create_trade(request)

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
    price = Helper.get_current_price(currency)
    # TODO: fix the price for pending trades -don't add price for pending trades, add when the trade start only binary options
    # TODO: load currency pair from currency_pairs table and add currency paris there
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
    trade_end_time = Trading.get_trade_end_time(time_to_close, end_date, end_time, time_slot, time_count, start,
                                                trade_start_time)

    # print(trade_start_time)
    # return
    error_messages.extend(Trading.validate_def_start_end_dates(trade_start_time, trade_end_time))
    error_messages.extend(Trading.validate_close_time_day(trade_end_time))
    error_messages.extend(Trading.validate_start_time_day(trade_start_time))

    purchase_type = Trading.get_trade_type(purchase)
    status = Trading.get_trade_status(start)

    print(error_messages)
    if error_messages:
        return error_messages
    # create new binary trade here

    time_now_formatted = Helper.get_current_time_formatted()
    time_now = datetime.strptime(time_now_formatted, '%Y-%m-%d %H:%M:%S.%f%z')
    changes_allowed_time = Trading.get_trade_changing_blocked_time(trade_start_time, trade_end_time)

    current_user = Helper.get_user_by_id(user_id)

    # print(trade_start_time)
    # print(Helper.get_time_formatted(trade_start_time))

    # use_trade = UserTransactionsIdBinary(user_id=user_id, created_date=time_now)
    user_transaction = TransactionsByUser(user_id=user_id, created_date=time_now)

    user_transaction.save()

    # new_d = time_now.strftime("%Y-%m-%d %H:%M:%S.%f%z")
    # print(new_d)
    # return
    cursor = connection.cursor()
    # q = f"SELECT * FROM user_transactions_id_binary WHERE user_id = {user_id} and created_date = '{time_now_formatted}'"
    q = f"SELECT * FROM transactions_by_user WHERE user_id = {user_id} and created_date = '{time_now_formatted}'"
    # print(q)

    transaction_id = cursor.execute(q)
    transaction_id = transaction_id[0]["id"]

    # trade = UserTransactionsBinary(id=transaction_id, user_id=user_id, created_date=time_now,
    #                                trade_type=trade_type, purchase_type=purchase_type,
    #                                currency=currency, staring_price=price, amount=float(amount),
    #                                start_time=trade_start_time, end_time=trade_end_time, status=status)
    # trade.save()
    # trades_by_status = TransactionsByStatusBinary(id=transaction_id, user_id=user_id, created_date=time_now,
    #                                               trade_type=trade_type, purchase_type=purchase_type,
    #                                               currency=currency, staring_price=price, amount=float(amount),
    #                                               start_time=trade_start_time, end_time=trade_end_time, status=status)
    #
    # trades_by_status.save()

    # trade = UserTransactions(transaction_id=transaction_id, user_id=user_id, created_date=time_now,
    #                          trade_type=Types.BINARY.value,
    #                          purchase_type=purchase_type, currency=currency, staring_price=price, amount=float(amount),
    #                          start_time=trade_start_time, end_time=trade_end_time,
    #                          changes_allowed_time=changes_allowed_time, outcome=Outcome.NONE.value, status=status)
    # trade.save()
    user_transactions = f"insert into user_transactions (transaction_id, user_id,created_date," \
                        f"trade_type,purchase_type, currency,staring_price,amount,start_time,end_time," \
                        f"changes_allowed_time,outcome,status) values ({transaction_id},{user_id}," \
                        f"'{time_now_formatted}','{Types.BINARY.value}'," \
                        f"'{purchase_type}','{currency}',{float(price)},{float(amount)}," \
                        f"'{Helper.get_time_formatted(trade_start_time)}','{Helper.get_time_formatted(trade_end_time)}'," \
                        f"'{Helper.get_time_formatted(changes_allowed_time)}','{Outcome.NONE.value}','{status}')"
    # print(user_transactions)
    cursor.execute(user_transactions)

    state_transactions = TransactionsByState(transaction_id=transaction_id, user_id=user_id,
                                             purchase_type=purchase_type, currency=currency, outcome=Outcome.NONE.value,
                                             status=status, created_date=time_now, amount=float(amount),
                                             trade_type=Types.BINARY.value)
    state_transactions.save()

    # transactions_by_start_time = TransactionsByStartTime(transaction_id=transaction_id, user_id=user_id, status=status,
    #                                                      start_time=Helper.get_time_formatted(trade_start_time))
    # transactions_by_start_time.save()

    transactions_by_start_time = f"INSERT INTO transactions_by_start_time (transaction_id,user_id,status,start_time) " \
                                 f"VALUES ({transaction_id},{user_id},'{status}'," \
                                 f"'{Helper.get_time_formatted(trade_start_time)}')"

    cursor.execute(transactions_by_start_time)

    # transactions_by_end_time = TransactionsByEndTime(transaction_id=transaction_id, user_id=user_id, status=status,
    #                                                  end_time=Helper.get_time_formatted(trade_end_time),
    #                                                  trade_type=Types.BINARY.value)
    #
    # transactions_by_end_time.save()
    transactions_by_end_time = f"INSERT INTO transactions_by_end_time (transaction_id,user_id,status,end_time," \
                               f"trade_type) VALUES ({transaction_id},{user_id},'{status}'," \
                               f"'{Helper.get_time_formatted(trade_end_time)}','{Types.BINARY.value}')"

    cursor.execute(transactions_by_end_time)

    # transactions_changes_allowed_time = TransactionsChangesAllowedTime(transaction_id=transaction_id, user_id=user_id,
    #                                                                    status=status,
    #                                                                    changes_allowed_time=Helper.get_time_formatted(
    #                                                                        changes_allowed_time))
    # transactions_changes_allowed_time.save()

    transactions_changes_allowed_time = f"INSERT INTO transactions_changes_allowed_time " \
                                        f"(transaction_id,user_id,status,changes_allowed_time) " \
                                        f"VALUES ({transaction_id},{user_id},'{status}'," \
                                        f"'{Helper.get_time_formatted(changes_allowed_time)}')"

    cursor.execute(transactions_changes_allowed_time)

    # update account balance
    updated_amount = float(current_user['vcurrency']) - float(amount)
    user_vcurrency = f"UPDATE  user_by_id SET vcurrency = {updated_amount} WHERE id = {user_id}"
    cursor.execute(user_vcurrency)
    Helper.store_state_value(user_id, StatKeys.BALANCE.value, amount, Helper.get_today_date())


def statements(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'statements.html', data)


def charts(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        pass
    data['auth'] = ac.is_user_logged_in()
    return render(request, 'charts.html', data)


def logout(request):
    ac = Authentication(request)
    if ac.is_user_logged_in():
        ac.logout()
    return redirect('/login')
