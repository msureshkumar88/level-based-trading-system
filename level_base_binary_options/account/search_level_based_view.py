from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from utilities.purchase_type import PurchaseTypes
from utilities.helper import Helper

from django.db import connection

def level_based_search(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    data = dict()
    if request.method == "POST":
        search(request)

    purchase_type = []
    [purchase_type.append(e.value) for e in PurchaseTypes]

    data['purchase_type'] = purchase_type
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


def search_all_inputs(request):
    for filed in request.POST:
        if filed != 'csrfmiddlewaretoken' and request.POST[filed]:
            return []
    return ["Nothing to search or filter"]
