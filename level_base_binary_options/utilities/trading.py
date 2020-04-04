from .trade_status import Status
from datetime import datetime
from datetime import timedelta
from django.db import connection


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