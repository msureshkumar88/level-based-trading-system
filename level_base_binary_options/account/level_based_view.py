from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime
from datetime import timedelta
from django.http import JsonResponse

from utilities.helper import Helper

from .models import LevelBasedById
from .models import UsersOwnedLevels
from .models import LevelBasedByStatus
from .models import UsersOwnedLevelsStatus
from .models import UserTransactionsIdLevels

from .models import TransactionsByUser

from utilities.trading import Trading
from utilities.trade_status import Status
from utilities.trade_outcome import Outcome
from utilities.trade_type import Types
from utilities.trade_levels import Levels
from utilities.state_keys import StatKeys

from django.db import connection

import re
import decimal

import json


def levels(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    data = dict()
    data = Trading.load_static_data()
    if request.method == "POST":
        data['errors'] = create_trade(request)
    data['auth'] = ac.is_user_logged_in()
    user_id = ac.get_user_session()
    data['current_user'] = user_id
    return render(request, 'level_based.html', data)


# TODO: trade closing date cannot be a weekend - because on closing price available
def create_trade(req):
    post = req.POST
    currency = post['currency']
    time_to_close = post['time_to_close']
    time_slot = post['time_slot']
    time_count = post['time_count']
    end_date = post['end_date']
    end_time = post['end_time']
    amount = post['amount']
    gap_pips = post['gap_pips']
    select_level = post['select_level']
    purchase = post['purchase']
    trade_type = 'levels'
    start_time = datetime.now()

    price = Helper.get_current_price(currency)
    ac = Authentication(req)
    user_id = ac.get_user_session()

    trade_start_time = datetime.now()
    error_messages = []
    error_messages.extend(Trading.validate_currency(currency))
    error_messages.extend(validate_pip_gaps(gap_pips))
    error_messages.extend(validate_levels(select_level))
    error_messages.extend(Trading.validate_time_to_close(time_to_close))
    error_messages.extend(Trading.validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time))
    error_messages.extend(Trading.validate_amount(amount, user_id))
    error_messages.extend(validated_end_date(time_to_close, end_date, end_time, time_slot, time_count, start_time))
    # price_to_zeroes(str(1.02065))
    # gap_pips_to_float(str(1.02065),str(10))
    # return
    # print(calculate_levels(currency, gap_pips, purchase))
    # final method to get selected levels
    levels_price = get_price_range_by_level(currency, gap_pips, purchase)

    # final method to get selected level
    selected_level = get_selected_level(select_level, currency, gap_pips, purchase)

    # final method to get trade closing time
    trade_closing_time = get_trade_end_time(time_to_close, end_date, end_time, time_slot, time_count, start_time)
    error_messages.extend(Trading.validate_close_time_day(trade_closing_time))

    # encode as a json string
    # cc = json.dumps(levels_price)
    # decode a json string
    # pp = json.loads(cc)

    if error_messages:
        # print(error_messages)
        return JsonResponse(Helper.get_json_response(False, {}, error_messages))
    # time_now = datetime.now()
    changes_allowed_time = Trading.get_trade_changing_blocked_time(start_time, trade_closing_time)
    level_owners = get_level_owner(select_level, user_id)

    time_now_formatted = Helper.get_current_time_formatted()

    time_now = datetime.strptime(time_now_formatted, '%Y-%m-%d %H:%M:%S.%f%z')

    purchase_type = Trading.get_trade_type(purchase)

    # user_transactions_id_levels = UserTransactionsIdLevels(user_id=user_id, created_date=time_now)
    # user_transactions_id_levels.save()

    available_levels = get_available_levels(Levels.levels.value, select_level)

    current_user = Helper.get_user_by_id(user_id)
    user_currency = current_user['currency']
    user_transaction = TransactionsByUser(user_id=user_id, created_date=time_now)
    user_transaction.save()

    # query = f"SELECT * FROM user_transactions_id_levels WHERE user_id = {user_id} and created_date = '{time_now_formatted}'"

    query = f"SELECT * FROM transactions_by_user WHERE user_id = {user_id} and created_date = '{time_now_formatted}'"
    cursor = connection.cursor()
    transaction_id = cursor.execute(query)
    transaction_id = transaction_id[0]["id"]

    user_transactions = f"INSERT INTO user_transactions " \
                        f"(transaction_id,user_id,created_date,trade_type,purchase_type,currency,staring_price,amount," \
                        f"start_time,end_time,changes_allowed_time,outcome,status,level_pips, levels_price,level_owners," \
                        f"join_date,level_start_price,level_end_price,level_selected,created_by,child," \
                        f"available_levels,amount_currency) " \
                        f"VALUES " \
                        f"({transaction_id},{user_id},'{time_now_formatted}','{Types.LEVELS.value}','{purchase_type}'," \
                        f"'{currency}',{float(price)},{float(amount)},'{Helper.get_time_formatted(trade_start_time)}'," \
                        f"'{Helper.get_time_formatted(trade_closing_time)}'," \
                        f"'{Helper.get_time_formatted(changes_allowed_time)}','{Outcome.NONE.value}'," \
                        f"'{Status.STARTED.value}',{int(gap_pips)},'{json.dumps(levels_price)}','{level_owners}'," \
                        f"'{time_now_formatted}',{selected_level['range'][0]},{selected_level['range'][1]}," \
                        f"{selected_level['level']},{user_id},{False},{available_levels},'{current_user['currency']}')"
    cursor.execute(user_transactions)

    transactions_by_state = f"INSERT INTO transactions_by_state " \
                            f"(transaction_id,user_id,currency,purchase_type,outcome,status,created_date,amount," \
                            f"trade_type) " \
                            f"VALUES " \
                            f"({transaction_id},{user_id},'{currency}','{purchase_type}','{Outcome.NONE.value}'," \
                            f"'{Status.STARTED.value}','{time_now_formatted}',{float(amount)},'{Types.LEVELS.value}')"
    cursor.execute(transactions_by_state)

    transactions_levels_status = f"INSERT INTO transactions_levels_status " \
                                 f"(transaction_id,user_id,outcome,purchase_type,currency,status,created_date,amount," \
                                 f"trade_type,start_time,end_time,available_levels,amount_currency) " \
                                 f"VALUES " \
                                 f"({transaction_id},{user_id},'{Outcome.NONE.value}','{purchase_type}','{currency}'," \
                                 f"'{Status.STARTED.value}','{time_now_formatted}',{float(amount)}," \
                                 f"'{Types.LEVELS.value}','{Helper.get_time_formatted(trade_start_time)}'," \
                                 f"'{Helper.get_time_formatted(trade_closing_time)}',{available_levels}, '{user_currency}')"

    cursor.execute(transactions_levels_status)

    transactions_by_end_time = f"INSERT INTO transactions_by_end_time " \
                               f"(transaction_id,user_id,status,trade_type,end_time) " \
                               f"VALUES " \
                               f"({transaction_id},{user_id},'{Status.STARTED.value}','{Types.LEVELS.value}'," \
                               f"'{Helper.get_time_formatted(trade_closing_time)}')"

    cursor.execute(transactions_by_end_time)

    transactions_changes_allowed_time = f"INSERT INTO transactions_changes_allowed_time " \
                                        f"(transaction_id,user_id,status,changes_allowed_time) " \
                                        f"VALUES " \
                                        f"({transaction_id},{user_id},'{Status.STARTED.value}'," \
                                        f"'{Helper.get_time_formatted(changes_allowed_time)}')"

    cursor.execute(transactions_changes_allowed_time)

    level_based_user_counts = f"INSERT INTO level_based_user_counts " \
                              f"(transaction_id,user_count) " \
                              f"VALUES " \
                              f"({transaction_id},1)"

    cursor.execute(level_based_user_counts)

    level_based_user_levels = f"INSERT INTO level_based_user_levels " \
                              f"(transaction_id,level_number) " \
                              f"VALUES " \
                              f"({transaction_id},{selected_level['level']})"

    cursor.execute(level_based_user_levels)

    level_based_by_user_id = f"INSERT INTO level_based_by_user_id " \
                             f"(transaction_id,owner,user_id) " \
                             f"VALUES " \
                             f"({transaction_id},{True},{user_id})"

    cursor.execute(level_based_by_user_id)

    updated_amount = float(current_user['vcurrency']) - float(amount)
    # update account balance
    user_vcurrency = f"UPDATE  user_by_id SET vcurrency = {updated_amount} WHERE id = {user_id}"
    cursor.execute(user_vcurrency)
    Helper.store_state_value(user_id, StatKeys.BALANCE.value, amount, 'subtract')
    Helper.store_state_value(user_id, StatKeys.NUM_TRADES.value, 1, 'add')
    Helper.store_state_value(user_id, StatKeys.LEVELS.value, 1, 'add')
    Trading.save_purchase_stats(user_id, purchase_type)
    Trading.save_levels_stats(user_id, select_level)
    Trading.save_levels_general_stats(user_id, select_level, amount, purchase_type)
    # levels_by_id = LevelBasedById(transaction_id=transaction_id, created_date=time_now, created_by=user_id,
    #                               purchase_type=purchase_type,
    #                               currency=currency, staring_price=float(price), amount=float(amount),
    #                               start_time=start_time, end_time=trade_closing_time,
    #                               changes_allowed_time=changes_allowed_time, status=Status.STARTED.value,
    #                               level_pips=int(gap_pips), levels_price=json.dumps(levels_price),
    #                               level_owners=level_owners, user_count=1)
    # levels_by_id.save()

    # users_owned_levels = UsersOwnedLevels(user_id=user_id, transaction_id=transaction_id, created_date=time_now,
    #                                       currency=currency,
    #                                       level_selected=selected_level["level"],
    #                                       level_start_price=selected_level["range"][0],
    #                                       level_end_price=selected_level["range"][1], owner=True,
    #                                       status=Status.STARTED.value,
    #                                       changes_allowed_time=changes_allowed_time, staring_price=float(price),
    #                                       start_time=start_time, end_time=trade_closing_time, amount=float(amount), outcome=Outcome.NONE.value)
    #
    # users_owned_levels.save()
    #
    # level_based_by_status = LevelBasedByStatus(status=Status.STARTED.value, transaction_id=transaction_id,
    #                                            created_date=time_now,
    #                                            purchase_type=purchase_type, currency=currency,
    #                                            staring_price=float(price), amount=float(amount),
    #                                            start_time=start_time, end_time=trade_closing_time,
    #                                            changes_allowed_time=changes_allowed_time,
    #                                            level_pips=int(gap_pips), levels_price=json.dumps(levels_price),
    #                                            level_owners=level_owners,
    #                                            user_count=1)
    # level_based_by_status.save()
    #
    # users_owned_levels_status = UsersOwnedLevelsStatus(status=Status.STARTED.value, user_id=user_id,
    #                                                    transaction_id=transaction_id,
    #                                                    created_date=time_now,
    #                                                    currency=currency,
    #                                                    staring_price=float(price), amount=float(amount),
    #                                                    level_selected=selected_level["level"],
    #                                                    level_start_price=selected_level["range"][0],
    #                                                    level_end_price=selected_level["range"][1], owner=True,
    #                                                    start_time=start_time, end_time=trade_closing_time,
    #                                                    changes_allowed_time=changes_allowed_time,
    #                                                    level_pips=int(gap_pips), outcome=Outcome.NONE.value)
    # users_owned_levels_status.save()
    return JsonResponse(Helper.get_json_response(True, {'transaction_id': str(transaction_id), "user_id": str(user_id)},
                                                 ['Trade created successfully']))


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


def validated_end_date(time_to_close, end_date, end_time, time_slot, time_count, start_time):
    if not time_to_close or not end_date or not end_time or not time_count:
        return []

    if time_to_close == 'end_time':
        end_time = Trading.make_date_time_stamp(end_date, end_time)
        if not Trading.validate_binary_trade_times(end_time):
            return ["Trade ending date should be a future date"]
        # Enable this if trade closing wants be more than 15 minutes
        # minutes_diff = (end_time - start_time).total_seconds() / 60.0
        # if minutes_diff < 15:
        #     return ["The trade closing date should be place at lease 15 minutes in the future"]
        return []

    time_count = int(time_count)
    if time_count < 1:
        return ["the duration should be at lease 1"]
    # Enable this if trade closing wants be more than 15 minutes
    # if (time_slot == "minutes" and time_count < 15):
    #     return ["When minutes are selected the duration should be at least 15"]
    return []


def get_selected_level(level, currency, gap, purchase):
    if not gap or not currency:
        return []
    level_gaps = get_price_range_by_level(currency, gap, purchase)
    return list(filter(lambda obj: obj['level'] == int(level), level_gaps))[0]


##
# [{'level': 1, 'range': ['1.00000', '1.00010']}, {'level': 2, 'range': ['1.00010', '1.00020']},
# {'level': 3, 'range': ['1.00020', '1.00030']}, {'level': 4, 'range': ['1.00030', '1.00040']}]
def get_price_range_by_level(currency, gap, purchase):
    if not currency or not gap or not purchase:
        return []
    level_gaps = []
    price = Helper.get_current_price(currency)
    price_gaps = calculate_levels(price, gap, purchase)

    # ['1.00010', '1.00020', '1.00030', '1.00040']
    for p in range(1, 5):
        gap = dict()
        gap["level"] = p
        if p == 1:
            gap["range"] = [price, price_gaps[0]]
            level_gaps.append(gap)
            continue
        gap["range"] = [price_gaps[p - 2], price_gaps[p - 1]]
        level_gaps.append(gap)
    return level_gaps


def calculate_levels(price, gap, purchase):
    # get number of decimal points - returned a negative value
    d = decimal.Decimal(price)

    # convert negative number of decimal points to positive
    decimal_point = abs(d.as_tuple().exponent)

    # create dynamic decimal point regex
    reg = "{:." + str(decimal_point) + "f}"

    price_list = []
    for p in range(1, 5):
        # as similar gaps between levels, multiply gap by each level upto 4 levels
        gap_multiplied = int(gap) * p

        # convert integer gap to matching float value by price
        price_to_add = gap_pips_to_float(price, gap_multiplied)

        level_price = ""
        if purchase == 'Buy':
            # if purchase is buy then add gap value
            level_price = float(price) + float(price_to_add)
        if purchase == 'Sell':
            # if purchase is sell then subtract gap value
            level_price = float(price) - float(price_to_add)
        # format new price level decimal point the same as original price
        price_list.append(reg.format(level_price))
    return price_list


##
#  replace all the digits with 0
#  convert 1.25360 as 0.00000
def price_to_zeroes(price):
    return re.sub(r"[0-9]", "0", str(price))


##
# convert integer gap to matching float value by price
# convert gap 10 pips as 0.00010
def gap_pips_to_float(price, pips):
    # convert float price to string
    pips = str(pips)

    # replace all the digits with 0
    zero_priced = price_to_zeroes(price)

    # remove last few digits dynamically according count of digits in the gap
    # add gap number to the end
    # convert gap 10 pips as 0.00010
    return zero_priced[:-len(pips)] + pips


# generate ending time
def get_trade_end_time(time_to_close, date, time, time_slot, time_count, start_time):
    if not time_to_close or not date or not time or not time_slot or not time_count or not start_time:
        return []
    if time_to_close == 'end_time':
        if Trading.validate_binary_trade_times(Trading.make_date_time_stamp(date, time)):
            return Trading.make_date_time_stamp(date, time)
        return ""
    time_count = int(time_count)
    # Enable this if trade closing wants be more than 15 minutes
    # if (time_slot == "minutes" and time_count < 15) or time_count < 1:
    #     return ""

    if time_count < 1:
        return ""
    # Remove this this if trade closing wants be more than 15 minutes
    if time_slot == "seconds":
        return start_time + timedelta(seconds=time_count)
    if time_slot == "minutes":
        return start_time + timedelta(minutes=time_count)
    if time_slot == "hours":
        return start_time + timedelta(hours=time_count)
    if time_slot == "days":
        return start_time + timedelta(days=time_count)


def get_level_owner(selected_level, user_id):
    owner = dict()
    owner["user_id"] = user_id
    owner["selected_level"] = selected_level
    owners = [owner]
    return json.dumps(owners)


def get_available_levels(level_list, selected_level):
    all_levels = level_list.copy()
    all_levels.remove(int(selected_level))
    return all_levels
