import hashlib
import requests
import csv
import time
import pytz
from time import gmtime, strftime
from datetime import datetime
from datetime import date
from django.db import connection
from currency_converter import CurrencyConverter

from .purchase_type import PurchaseTypes
from .trade_levels import Levels
from .state_keys import StatKeys


class Helper:
    @classmethod
    def password_encrypt(cls, password):
        h = hashlib.new('ripemd160')
        h.update(password.encode('utf-8'))
        return h.hexdigest()

    @classmethod
    def get_fx_feed_url(cls):
        return 'https://webrates.truefx.com/rates/connect.html?f=csv'

    @classmethod
    def fx_request_url(cls, pair):
        return Helper.get_fx_feed_url() + "&c=" + pair

    @classmethod
    def get_current_price(cls, currency):
        # TODO: should be returned as string
        # TODO: check this function to get the value from database
        # TODO: change this function to work with get_current_price_instance
        # return '1.00000'
        with requests.Session() as s:
            download = s.get(Helper.fx_request_url(currency))

            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                if len(row) != 0:
                    bid = float(row[2] + row[3])
                    offer = float(row[4] + row[5])
                    mid_price = (bid + offer) / 2
                    return "%.5f" % mid_price

    @classmethod
    def get_current_time_formatted(cls):
        time_now = datetime.now(pytz.utc)
        mils = time_now.strftime('%f')[:-3]
        zone = strftime("%z", gmtime())
        if strftime("%z", gmtime()) == "-0000":
            zone = "+0000"
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.') + mils + zone

    @classmethod
    def get_time_formatted(cls, date_time):
        mils = date_time.strftime('%f')[:-3]
        zone = strftime("%z", gmtime())
        if strftime("%z", gmtime()) == "-0000":
            zone = "+0000"
        return date_time.strftime('%Y-%m-%d %H:%M:%S.') + mils + zone

    @classmethod
    # returns user details by user_id
    def get_user_by_id(cls, user_id):
        cursor = connection.cursor()
        user = cursor.execute(f"SELECT * FROM user_by_id where id = {user_id}")
        return user[0]

    @classmethod
    def get_countries(cls):
        cursor = connection.cursor()
        country = cursor.execute("SELECT * FROM country")
        return country

    @classmethod
    def get_currency_pairs(cls):
        cursor = connection.cursor()
        currency_pairs = cursor.execute("SELECT * FROM currency_pairs")
        return currency_pairs

    @classmethod
    def get_currency_pairs_list(cls):
        pairs = []
        [pairs.append(p['value']) for p in Helper.get_currency_pairs()]
        return pairs

    @classmethod
    def get_purchase_type_list(cls):
        purchase_type = []
        [purchase_type.append(e.value) for e in PurchaseTypes]
        return purchase_type

    @classmethod
    def get_trade_level_list(cls):
        return Levels.levels.value

    @classmethod
    def get_currency(cls):
        cursor = connection.cursor()
        currency = cursor.execute("SELECT * FROM currency")
        return currency

    @classmethod
    def convert_currency(cls, amount, from_currency, to_currency):
        c = CurrencyConverter()
        amount = float(c.convert(amount, from_currency.upper(), to_currency.upper()))
        return "%.2f" % round(amount, 2)

    @classmethod
    def get_json_response(cls, status, data, message):
        response = dict()
        response['status'] = status
        response['data'] = data
        response['message'] = message
        return response

    @classmethod
    def get_state_by_key(cls, user_id, state_key, date_val):
        cursor = connection.cursor()
        result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                f"AND type = '{state_key}' and date = '{date_val}'")

        if result:
            return result[0]
        return []

    @classmethod
    def store_state_value(cls, user_id, state_key, state_value, operation):
        today_date = Helper.get_today_date()
        cursor = connection.cursor()
        state = Helper.get_state_by_key(user_id, state_key, today_date)

        new_value = state_value

        if not state:
            if state_key == StatKeys.BALANCE.value:
                user_data = Helper.get_user_by_id(user_id)
                new_value = user_data['vcurrency']

            cursor.execute(f"INSERT INTO states (user_id,type,date,value) "
                           f"VALUES ({user_id},'{state_key}','{today_date}',{new_value})")
            return

        if operation == 'subtract':
            new_value = float(state['value']) - float(state_value)
        if operation == 'add':
            new_value = float(state['value']) + float(state_value)

        cursor.execute(f"INSERT INTO states (user_id,type,date,value) "
                       f"VALUES ({user_id},'{state_key}','{today_date}',{new_value})")

    @classmethod
    def get_state_by_date_range(cls, user_id, state_key, start_date, end_date):
        cursor = connection.cursor()
        result = cursor.execute(f"SELECT * FROM states WHERE user_id = {user_id} "
                                f"AND type = '{state_key}' and date >= '{start_date}' "
                                f"AND and date <= '{end_date}'")

        return result

    @classmethod
    def get_today_date(cls):
        return date.today().strftime("%Y-%m-%d")

    @classmethod
    def get_general_stat_by_key(cls, user_id, key):
        cursor = connection.cursor()
        result = cursor.execute(f"SELECT * FROM general_states WHERE user_id = {user_id} "
                                f"AND type = '{key}'")
        result = result.one()
        if result:
            return result["value"]
        return 0

    @classmethod
    def save_general_stat_by_key(cls, user_id, key, value):
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO general_states "
                       f"(user_id, type, value) "
                       f"VALUES "
                       f"({user_id},'{key}', {value})")

    @classmethod
    def get_general_stat_by_user(cls,user_id, key):
        cursor = connection.cursor()
        result = cursor.execute(f"SELECT * FROM general_states WHERE user_id = {user_id} and type = '{key}'")
        result = result.one()
        if result:
            return result["value"]
        return 0

    @classmethod
    def get_latest_pending_trades(cls, user_id):
        cursor = connection.cursor()
        result = cursor.execute(f" select * from transactions_by_state "
                                f"where user_id = {user_id} "
                                f"and status='pending' limit 5")
        return result.all()
