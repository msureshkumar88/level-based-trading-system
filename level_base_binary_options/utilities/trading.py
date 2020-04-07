from .trade_status import Status
from datetime import datetime
from datetime import timedelta
from django.db import connection

from .helper import Helper

class Trading:
    # generate trade start time
    @classmethod
    def get_trade_start_time(cls, start, date, time):
        if start == "start now":
            return datetime.now()
        if Trading.validate_binary_trade_times(Trading.make_date_time_stamp(date, time)):
            return Trading.make_date_time_stamp(date, time)
        return ""

    # generate trade end time
    @classmethod
    def get_trade_end_time(cls, time_to_close, date, time, time_slot, time_count, start, start_time):
        if time_to_close == 'end_time':
            if Trading.validate_binary_trade_times(Trading.make_date_time_stamp(date, time)):
                return Trading.make_date_time_stamp(date, time)
            return ""
        time_count = int(time_count)
        adding_time = datetime.now()
        if start == "start later":
            adding_time = start_time

        if (time_slot == "seconds" and time_count < 5) or time_count < 1:
            return ""
        if time_slot == "seconds":
            return adding_time + timedelta(seconds=time_count)
        if time_slot == "minutes":
            return adding_time + timedelta(minutes=time_count)
        if time_slot == "hours":
            return adding_time + timedelta(hours=time_count)
        if time_slot == "days":
            return adding_time + timedelta(days=time_count)

    # return static data for trade creation UI
    @classmethod
    def load_static_data(cls):
        cursor = connection.cursor()
        currencies = cursor.execute("SELECT * FROM currency")
        duration = cursor.execute("SELECT * FROM duration")

        data = dict()
        data['currency'] = currencies
        data['duration'] = duration
        data['today_date'] = datetime.now().strftime("%Y-%m-%d")
        data['time_now'] = datetime.now().strftime("%H:%M")
        return data

    # check whether selected dates are greater than current date and time
    @classmethod
    def validate_binary_trade_times(cls, date_time):
        if datetime.now() >= date_time:
            return False
        return True

    # convert date and time to system's format
    @classmethod
    def make_date_time_stamp(cls, date, time):
        return datetime.strptime(date + " " + time + ":00", '%Y-%m-%d %H:%M:%S')

    @classmethod
    def format_date_time(cls, datetime):
        pass

    # get user selected trade type
    @classmethod
    def get_trade_type(cls, purchase):
        if purchase == 'Buy':
            return 'buy'
        return 'sell'

    # get the flag that determine trade start now or later
    @classmethod
    def get_trade_status(cls, start):
        if start == "start now":
            return Status.STARTED.value
        return Status.PENDING.value

    # validate if the end date is greater start date
    @classmethod
    def validate_def_start_end_dates(cls, start_date, end_date):
        print(start_date)
        print(end_date)
        if start_date >= end_date:
            return "Trade closing date must be future date"
        return ""

    @classmethod
    # generate middle time between trade start and end time
    # after this time edit trade is not allowed
    def get_trade_changing_blocked_time(cls, start_date, end_date):
        return start_date + (end_date - start_date) / 2

    @classmethod
    # validate binary options trade start date and time
    def validate_start_date(cls, start, start_date, start_time):
        if start == "start later":
            if not start_date and not start_time:
                return ["please select trade start date and time "]
            if not start_date:
                return ["Please select trade start date"]
            if not start_time:
                return ["Please select trade start time"]
        return []

    @classmethod
    # validate currency selection
    def validate_currency(cls,currency):
        if not currency:
            return ['Please select a currency pair']
        return []

    @classmethod
    # validate trade closing time selection
    def validate_time_to_close(cls, time_to_close):
        if not time_to_close:
            return ['Please select a closing type']
        return []

    @classmethod
    # validate each trade closing option
    def validate_closing_types(cls, time_to_close, time_slot, time_count, end_date, end_time):
        if time_to_close == "duration":
            if not time_slot and not time_count:
                return ['Please fill both type of end time and duration units']
            if not time_slot:
                return ['Please select a type of duration']
            if not time_count:
                return ['Please enter end duration']
            if not time_count.isnumeric():
                return ['Please enter a valid units']
        if time_to_close == "end_time":
            if not end_date and not end_time:
                return ['Please fill both trade end date and time']
            if not end_date:
                return ['Please fill trade end date']
            if not end_time:
                return ['Please fill trade end time']
        return []

    @classmethod
    def validate_amount(cls, amount, user_id):
        if not amount:
            return ['Please enter amount']
        if not amount.isnumeric():
            return ['Please enter a valid amount']
        amount = float(amount)
        if amount < 1:
            return ['Amount should be greater than 0']
        user = Helper.get_user_by_id(user_id)
        if user['vcurrency'] < amount:
            return ['Do not have enough fund please add funds']
        return []

