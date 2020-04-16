from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from utilities.helper import Helper

from django.db import connection

from utilities.trade_status import Status
from utilities.trade_levels import Levels


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

    print(initial_query)
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

    # print(error_messages)
    if error_messages:
        return error_messages


def validate_level_selection(selected_level):
    if not selected_level:
        return ["Please select a level"]
    return []


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


def validate_changes_allowed_time_exceeded():
    pass


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
