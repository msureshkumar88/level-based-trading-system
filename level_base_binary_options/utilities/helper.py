import hashlib
import requests
import csv
import time
import pytz
from time import gmtime, strftime
from datetime import datetime
from django.db import connection
from currency_converter import CurrencyConverter

from .purchase_type import PurchaseTypes
from .trade_levels import Levels


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
        user = cursor.execute("SELECT * FROM user_by_id where id =" + user_id)
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
        amount = float(c.convert(amount, from_currency, to_currency))
        return "%.2f" % round(amount, 2)
