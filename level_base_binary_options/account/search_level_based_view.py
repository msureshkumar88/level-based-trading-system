from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from utilities.helper import Helper

from django.db import connection

from utilities.trade_status import Status
from utilities.trade_levels import Levels
from utilities.state_keys import StatKeys
from utilities.trading import Trading

from datetime import datetime
import json


def level_based_search(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    data['results'] = []
    if request.method == "POST":
        form = request.POST['form']
        if form == "search":
            data['results'] = search(request)
        if form == "join":
            join(request)

    data['purchase_type'] = Helper.get_purchase_type_list()
    data['currency_pairs'] = Helper.get_currency_pairs()
    user_id = ac.get_user_session()
    current_user = Helper.get_user_by_id(user_id)
    data['user_currency'] = current_user["currency"]
    data['auth'] = ac.is_user_logged_in()
    return render(request, 'level_trade_search.html', data)


def search(request):
    currency = request.POST['currency']
    purchase_type = request.POST['purchase_type']
    closing_date = request.POST['closing_date']
    min_amount = request.POST['min_amount']
    max_amount = request.POST['max_amount']
    # TODO: Don't show user own trades show only from others
    error_messages = []
    error_messages.extend(search_all_inputs(request))
    print(error_messages)
    if error_messages:
        return error_messages

    ac = Authentication(request)
    user_id = ac.get_user_session()
    cursor = connection.cursor()
    single_status = f"('{Status.STARTED.value}')"
    initial_query = f"SELECT * FROM transactions_levels_status WHERE status in {single_status} "

    if currency:
        initial_query = initial_query + filter_where_currency_pair(currency)

    if not currency:
        initial_query = initial_query + filter_where_currency_pairs_in()
    # TODO: fix filters end_date before filtering purchase type
    # if purchase_type:
    #     initial_query = initial_query + filter_where_purchase_type(currency)
    #
    # if not purchase_type:
    #     initial_query = initial_query + filter_where_purchase_type_in()

    # TODO: extend  this search to work with trade closing date and amount range
    # TODO: don't show trades if trade change time is expired
    # print(initial_query)
    results = cursor.execute(initial_query)
    if not results:
        return []
    return results


def join(request):
    transaction_id = request.POST['trans']
    selected_level = request.POST['selected_level_' + transaction_id]
    error_messages = []
    error_messages.extend(validate_level_selection(selected_level))
    error_messages.extend(validate_level_already_taken(transaction_id, selected_level))
    error_messages.extend(validate_user_count_exceeded(transaction_id))

    parent_trade = get_parent_trade(transaction_id)
    ac = Authentication(request)
    user_id = ac.get_user_session()
    # print(parent_trade)
    error_messages.extend(validate_changes_allowed_time_exceeded(parent_trade["changes_allowed_time"]))
    print(error_messages)
    if error_messages:
        return error_messages
    current_user = Helper.get_user_by_id(user_id)
    # print(current_user)
    persist_join(user_id, transaction_id, parent_trade, selected_level, current_user)


def persist_join(user_id, transaction_id, parent_trade, selected_level, current_user):
    persist_user_transactions(user_id, transaction_id, parent_trade, selected_level)
    persist_transactions_by_state(transaction_id, user_id, parent_trade)
    persist_transactions_by_end_time(transaction_id, user_id, parent_trade)
    persist_transactions_changes_allowed_time(transaction_id, user_id, parent_trade)
    persist_level_based_user_counts(transaction_id)
    persist_level_based_user_levels(transaction_id, selected_level)
    persist_level_based_by_user_id(user_id, transaction_id)

    update_other_trades(transaction_id, user_id, selected_level, parent_trade)
    update_user_account_fields(user_id, current_user, parent_trade)
    save_stats(current_user, parent_trade, selected_level)


def persist_user_transactions(user_id, transaction_id, parent_trade, selected_level):
    current_user = Helper.get_user_by_id(user_id)

    converted_amount = Helper.convert_currency(parent_trade['amount'], parent_trade['amount_currency'],
                                               current_user['currency'])

    price_range = get_selected_level_price(parent_trade['levels_price'], selected_level)

    available_levels = get_available_levels(parent_trade['available_levels'], selected_level)

    level_owners = add_level_owners(parent_trade['level_owners'], user_id, selected_level)
    start_time = Helper.get_time_formatted(parent_trade['start_time'])
    end_time = Helper.get_time_formatted(parent_trade['end_time'])
    changes_allowed_time = Helper.get_time_formatted(parent_trade['changes_allowed_time'])
    created_date = Helper.get_time_formatted(parent_trade['created_date'])
    # print(changes_allowed_time)
    # return

    fields = "(transaction_id,user_id,created_date,trade_type,purchase_type,currency,staring_price," \
             "amount,amount_currency,start_time,end_time,changes_allowed_time,outcome,status,level_pips,levels_price,level_owners," \
             "join_date,level_start_price,level_end_price,level_selected,created_by,parent_id,child,available_levels)"

    values = f"({transaction_id},{user_id},'{created_date}','{parent_trade['trade_type']}'," \
             f"'{parent_trade['purchase_type']}','{parent_trade['currency']}',{parent_trade['staring_price']}," \
             f"{converted_amount},'{current_user['currency']}','{start_time}','{end_time}'," \
             f"'{changes_allowed_time}','{parent_trade['outcome']}','{parent_trade['status']}'," \
             f"{parent_trade['level_pips']},'{parent_trade['levels_price']}'," \
             f"'{level_owners}'," \
             f"'{Helper.get_current_time_formatted()}',{price_range['range'][0]},{price_range['range'][1]}," \
             f"{selected_level},{parent_trade['created_by']},{parent_trade['user_id']},{True}, {available_levels})"

    user_transactions = f"INSERT INTO user_transactions {fields} VALUES {values}"
    # print(user_transactions)
    cursor = connection.cursor()
    cursor.execute(user_transactions)


def persist_transactions_by_state(transaction_id, user_id, parent_trade):
    created_date = Helper.get_current_time_formatted()
    current_user = Helper.get_user_by_id(user_id)
    converted_amount = Helper.convert_currency(parent_trade['amount'], parent_trade['amount_currency'],
                                               current_user['currency'])

    fields = "(transaction_id,user_id,currency,purchase_type,outcome,status, created_date, amount, trade_type)"

    values = f"({transaction_id}, {user_id},'{parent_trade['currency']}','{parent_trade['purchase_type']}'," \
             f"'{parent_trade['outcome']}','{parent_trade['status']}','{created_date}',{converted_amount}," \
             f"'{parent_trade['trade_type']}')"

    transactions_by_state = f"INSERT INTO transactions_by_state {fields} VALUES {values}"
    cursor = connection.cursor()
    cursor.execute(transactions_by_state)


def persist_transactions_by_end_time(transaction_id, user_id, parent_trade):
    end_time = Helper.get_time_formatted(parent_trade['end_time'])
    fields = "(transaction_id, user_id,status,trade_type,end_time)"
    values = f"({transaction_id},{user_id},'{parent_trade['status']}','{parent_trade['trade_type']}','{end_time}')"

    transactions_by_end_time = f"INSERT INTO transactions_by_end_time {fields} VALUES {values}"
    cursor = connection.cursor()
    cursor.execute(transactions_by_end_time)


def persist_transactions_changes_allowed_time(transaction_id, user_id, parent_trade):
    changes_allowed_time = Helper.get_time_formatted(parent_trade['changes_allowed_time'])

    fields = "(transaction_id,user_id,status,changes_allowed_time)"
    values = f"({transaction_id},{user_id},'{parent_trade['status']}','{changes_allowed_time}')"

    transactions_changes_allowed_time = f"INSERT INTO transactions_changes_allowed_time {fields} VALUES {values}"
    cursor = connection.cursor()
    cursor.execute(transactions_changes_allowed_time)


def persist_level_based_user_counts(transaction_id):
    cursor = connection.cursor()
    current_count = f"SELECT * FROM level_based_user_counts WHERE transaction_id = {transaction_id}"
    current_count = cursor.execute(current_count)
    new_count = int(current_count[0]["user_count"]) + 1
    update = f"UPDATE level_based_user_counts SET user_count = {new_count} WHERE transaction_id = {transaction_id}"
    cursor.execute(update)


def persist_level_based_user_levels(transaction_id, selected_level):
    cursor = connection.cursor()
    level_based_user_levels = f"INSERT INTO level_based_user_levels (transaction_id,level_number) " \
                              f"VALUES ({transaction_id},{selected_level})"

    cursor.execute(level_based_user_levels)


def persist_level_based_by_user_id(user_id, transaction_id):
    cursor = connection.cursor()
    level_based_by_user_id = f"INSERT INTO level_based_by_user_id (transaction_id,owner,user_id) " \
                             f"VALUES ({transaction_id},{False},{user_id})"

    cursor.execute(level_based_by_user_id)


# update all other trades that have already joined - except current user's trade
# update level owners
# update available levels
def update_other_trades(transaction_id, user_id, selected_level, parent_trade):
    cursor = connection.cursor()
    level_based_by_user_id = f"SELECT * FROM level_based_by_user_id WHERE transaction_id = {transaction_id}"
    existing_trades = cursor.execute(level_based_by_user_id)

    current_user_trade = f"SELECT * FROM user_transactions WHERE transaction_id = {transaction_id} AND user_id = {user_id}"
    current_user_trade = cursor.execute(current_user_trade)
    current_user_trade = current_user_trade[0]

    for trade in existing_trades:
        # print("here")
        # print(trade['user_id'], user_id)
        if trade['user_id'] != user_id:
            # trade_reloaded_query = f"SELECT * FROM user_transactions WHERE " \
            #                        f"transaction_id = {transaction_id} AND user_id = {trade['user_id']}"
            #
            # trade_reloaded = cursor.execute(trade_reloaded_query)
            # trade_reloaded = trade_reloaded[0]
            #
            # available_levels = get_available_levels(current_user_trade["available_levels"], selected_level)
            # level_owners = add_level_owners(current_user_trade['level_owners'], user_id, selected_level)

            update = f"UPDATE user_transactions SET available_levels = {current_user_trade['available_levels']}" \
                     f",level_owners = '{current_user_trade['level_owners']}' " \
                     f"WHERE transaction_id = {transaction_id} and user_id = {trade['user_id']}"
            cursor.execute(update)
    #   update transactions_levels_status available_levels
    end_time = Helper.get_time_formatted(current_user_trade['end_time'])
    update_transactions_levels_status = f"UPDATE transactions_levels_status SET available_levels = " \
                                        f"{current_user_trade['available_levels']} " \
                                        f"WHERE status = '{parent_trade['status']}' " \
                                        f"AND currency = '{parent_trade['currency']}'" \
                                        f"AND end_time = '{end_time}' " \
                                        f"AND purchase_type = '{parent_trade['purchase_type']}' " \
                                        f"AND amount = {parent_trade['amount']} " \
                                        f"AND transaction_id = {parent_trade['transaction_id']} " \
                                        f"AND user_id = {parent_trade['user_id']}"

    # print(update_transactions_levels_status)
    cursor.execute(update_transactions_levels_status)


# update vcurrency in the user table
def update_user_account_fields(user_id, current_user, parent_trade):
    cursor = connection.cursor()
    converted_amount = Helper.convert_currency(parent_trade['amount'], parent_trade['amount_currency'],
                                               current_user['currency'])

    updated_amount = float(current_user['vcurrency']) - float(converted_amount)
    # update account balance
    update_user = f"UPDATE user_by_id SET vcurrency = {updated_amount} WHERE id = {user_id}"
    cursor.execute(update_user)


def save_stats(current_user, parent_trade, selected_level):
    converted_amount = Helper.convert_currency(parent_trade['amount'], parent_trade['amount_currency'],
                                               current_user['currency'])
    # print('converted_amount',converted_amount)
    Helper.store_state_value(current_user['id'], StatKeys.BALANCE.value, converted_amount, 'subtract')
    Helper.store_state_value(current_user['id'], StatKeys.NUM_TRADES.value, 1, 'add')
    Helper.store_state_value(current_user['id'], StatKeys.LEVELS.value, 1, 'add')
    Trading.save_purchase_stats(current_user['id'], parent_trade['purchase_type'])
    Trading.save_levels_stats(current_user['id'], selected_level)


def add_level_owners(current_owners, user_id, selected_level):
    current_owners = json.loads(current_owners)
    rec = dict()
    rec['user_id'] = user_id
    rec['selected_level'] = selected_level
    current_owners.append(rec)
    return json.dumps(current_owners)


def get_selected_level_price(ranges, selected_level):
    ranges = json.loads(ranges)
    for r in ranges:
        if int(r['level']) == int(selected_level):
            return r


def get_available_levels(available_levels, selected_level):
    available_levels_copy = available_levels.copy()
    # print(available_levels_copy)
    available_levels_copy.remove(int(selected_level))
    return available_levels_copy


def validate_level_selection(selected_level):
    if not selected_level:
        return ["Please select a level"]
    return []


# not allow to enter more than one level
def validate_level_already_taken(transaction_id, selected_level):
    if validate_level_selection(selected_level):
        return []
    cursor = connection.cursor()
    level_based_user_levels = f"SELECT * FROM level_based_user_levels WHERE " \
                              f"transaction_id = {transaction_id} AND level_number = {selected_level}"
    results = cursor.execute(level_based_user_levels)
    if results:
        return ["The level has already taken"]
    return []


def validate_changes_allowed_time_exceeded(allowed_time_exceed):
    if allowed_time_exceed <= datetime.now():
        return ["The trade has expired please try another one"]
    return []


def validate_user_count_exceeded(transaction_id):
    level_based_user_counts = f"SELECT * FROM level_based_user_counts WHERE " \
                              f"transaction_id = {transaction_id}"

    cursor = connection.cursor()
    results = cursor.execute(level_based_user_counts)
    if results[0]['user_count'] == len(Levels.levels.value):
        return ["Number of traders to this trade has exceeded, this trade is not available"]
    return []


# get the initial record of the level based trade to populate continually when user join
def get_parent_trade(transaction_id):
    user_count = f"SELECT * FROM level_based_by_user_id WHERE " \
                 f"transaction_id = {transaction_id} AND owner = {True}"
    cursor = connection.cursor()
    user_count_result = cursor.execute(user_count)

    user_transactions = f"SELECT * FROM user_transactions WHERE " \
                        f"transaction_id = {transaction_id} AND user_id = {user_count_result[0]['user_id']}"

    user_transactions_result = cursor.execute(user_transactions)
    return user_transactions_result[0]


def filter_where_currency_pair(currency_pair):
    single_currency = f"('{currency_pair}')"
    return f"AND currency in {single_currency} "


def filter_where_currency_pairs_in():
    return f"AND currency in {tuple(Helper.get_currency_pairs_list())} "


def filter_where_purchase_type(purchase_type):
    single_purchase_type = f"('{purchase_type}')"
    return f"AND purchase_type in {single_purchase_type} "


def filter_where_purchase_type_in():
    return f"AND purchase_type in {tuple(Helper.get_purchase_type_list())} "


# filter by trade closing time - get the results greater than minimum closing time
def filter_where_closing_time(closing_time):
    return f"AND end_time > '{closing_time}' "


# filter amount range
def filter_where_amount(min_amount, max_amount):
    return f"AND amount > {min_amount} AND amount < {max_amount} "


# TODO: filter when both amount and closing date submitted

def search_all_inputs(request):
    for filed in request.POST:
        if filed != 'csrfmiddlewaretoken' and request.POST[filed]:
            return []
    return ["Nothing to search or filter"]
