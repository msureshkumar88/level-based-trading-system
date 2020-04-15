from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from utilities.helper import Helper

from django.db import connection

from utilities.trade_status import Status


def level_based_search(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        search(request)

    data['purchase_type'] = Helper.get_purchase_type_list()
    data['currency_pairs'] = Helper.get_currency_pairs()

    return render(request, 'level_trade_search.html', data)


def search(request):
    currency = request.POST['currency']
    purchase_type = request.POST['purchase_type']
    closing_date = request.POST['closing_date']
    min_amount = request.POST['min_amount']
    max_amount = request.POST['max_amount']

    error_messages = []
    error_messages.extend(search_all_inputs(request))
    print(error_messages)
    if error_messages:
        return error_messages

    ac = Authentication(request)
    user_id = ac.get_user_session()
    cursor = connection.cursor()

    initial_query = f"SELECT * FROM transactions_by_state WHERE status = {Status.STARTED.value} "


def filter_where_currency_pair(currency_pair):
    return f"AND currency = '{currency_pair}' "


def filter_where_currency_pairs_in():
    return f"AND currency in {tuple(Helper.get_currency_pairs_list())} "


def filter_where_purchase_type(purchase_type):
    return f"AND purchase_type = '{purchase_type}' "


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
