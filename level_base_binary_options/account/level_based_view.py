from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime
from datetime import timedelta

from utilities.helper import Helper
from .models import UserTransactionsBinary
from .models import TransactionsByStatusBinary
from utilities.trading import Trading

import re
import decimal


def levels(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    data = dict()
    data = Trading.load_static_data()
    if request.method == "POST":
        create_trade(request)

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
    purchase = post['purchase']
    trade_type = 'levels'
    start_time = datetime.now()

    price = Helper.get_current_price(currency)
    ac = Authentication(req)
    user_id = ac.get_user_session()

    trade_start_time = datetime.now()
    error_messages = []
    error_messages.extend(validate_currency(currency))
    error_messages.extend(validate_pip_gaps(gap_pips))
    error_messages.extend(validate_levels(select_level))
    error_messages.extend(validate_time_to_close(time_to_close))
    error_messages.extend(validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time))
    error_messages.extend(validate_amount(amount,user_id))
    error_messages.extend(validated_end_date(time_to_close, end_date, end_time, time_slot, time_count, start_time))
    # price_to_zeroes(str(1.02065))
    # gap_pips_to_float(str(1.02065),str(10))
    # return
    # print(calculate_levels(currency, gap_pips, purchase))
    # final method to get selected levels
    # print(get_price_range_by_level(currency, gap_pips, purchase))
    # print(get_selected_level(select_level, currency, gap_pips, purchase))
    # final method to get trade closing time
    # print(get_trade_end_time(time_to_close, end_date, end_time, time_slot, time_count, start_time))
    print(error_messages)
    return
    if error_messages:
        # print(error_messages)
        return error_messages


def validate_currency(currency):
    if not currency:
        return ['Please select a currency pair']
    return []


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


def validate_time_to_close(time_to_close):
    if not time_to_close:
        return ['Please select a closing type']
    return []


def validate_closing_types(time_to_close, time_slot, time_count, end_date, end_time):
    if time_to_close == "Duration":
        if not time_slot:
            return ['Please select a type of duration']
        if not time_count:
            return ['Please enter end duration']
        if not time_slot and not time_count:
            return ['Please fill both type of end time and duration units']
    if time_to_close == "End Time":
        if not end_date:
            return ['Please fill trade end date']
        if not end_time:
            return ['Please fill trade end time']
        if not end_date and not end_time:
            return ['Please fill both trade end date and time']
    return []


def validate_amount(amount, user_id):
    if not amount:
        return ['Please enter amount']
    amount = float(amount)
    if amount < 1:
        return ['Amount should be greater than 0']
    user = Helper.get_user_by_id(user_id)
    if user['vcurrency'] < amount:
        return ['Do not have enough fund please add funds']
    return []


def validated_end_date(time_to_close, end_date, end_time, time_slot, time_count, start_time):
    if time_to_close == 'end_time':
        end_time = Trading.make_date_time_stamp(end_date, end_time)
        if not Trading.validate_binary_trade_times(end_time):
            return ["Trade ending date should be a future date"]
        minutes_diff = (end_time - start_time).total_seconds() / 60.0
        if minutes_diff < 15:
            return ["The trade closing date should be place at lease 15 minutes in the future"]
        return []

    time_count = int(time_count)
    if time_count < 1:
        return ["the duration should be at lease 1"]
    if (time_slot == "minutes" and time_count < 15):
        return ["When minutes are selected the duration should be at least 15"]
    return []


def get_selected_level(level, currency, gap, purchase):
    level_gaps = get_price_range_by_level(currency, gap, purchase)
    return list(filter(lambda person: person['level'] == int(level), level_gaps))[0]


##
# [{'level': 1, 'range': ['1.00000', '1.00010']}, {'level': 2, 'range': ['1.00010', '1.00020']},
# {'level': 3, 'range': ['1.00020', '1.00030']}, {'level': 4, 'range': ['1.00030', '1.00040']}]
def get_price_range_by_level(currency, gap, purchase):
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
    if time_to_close == 'end_time':
        if Trading.validate_binary_trade_times(Trading.make_date_time_stamp(date, time)):
            return Trading.make_date_time_stamp(date, time)
        return ""
    time_count = int(time_count)
    if (time_slot == "minutes" and time_count < 15) or time_count < 1:
        return ""
    if time_slot == "minutes":
        return start_time + timedelta(minutes=time_count)
    if time_slot == "hours":
        return start_time + timedelta(hours=time_count)
    if time_slot == "days":
        return start_time + timedelta(days=time_count)
