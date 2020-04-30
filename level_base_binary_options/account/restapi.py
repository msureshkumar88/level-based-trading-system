from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.db import connection
from datetime import datetime

from utilities.authentication import Authentication
from utilities.helper import Helper
from utilities.trading import Trading



def get_transaction(request):
    ac = Authentication(request)
    # if user is not logged in response user not exist
    if not ac.is_user_logged_in():
        return JsonResponse(Helper.get_json_response(False, [], ['Please login']))
    post = request.POST

    trade = Trading.get_transaction_by_id(post['transaction_ref'], post['trade_owner'])
    if not trade:
        return JsonResponse(Helper.get_json_response(False, [], ["Trade not available"]))
    user_id = ac.get_user_session()

    current_user = Helper.get_user_by_id(user_id)
    trade_data = dict()
    trade_data['contract_type'] = trade['trade_type']
    trade_data['transaction_ref'] = trade['transaction_id']
    trade_data['purchase_type'] = trade['purchase_type']
    trade_data['start_time'] = trade['start_time']
    trade_data['end_time'] = trade['end_time']
    trade_data['amount'] = Helper.convert_currency(trade['amount'] , trade['amount_currency'],current_user['currency'])
    trade_data['user_currency'] = current_user['currency']
    trade_data['staring_price'] = trade['staring_price']
    trade_data['closing_price'] = trade['closing_price']
    trade_data['outcome'] = trade['outcome']

    return JsonResponse(Helper.get_json_response(True, [trade_data], []))
