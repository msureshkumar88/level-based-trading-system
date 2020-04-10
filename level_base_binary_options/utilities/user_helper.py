import re
from django.db import connection


class UserHelper:
    @classmethod
    def validate_amount(cls, amount):
        if not amount:
            return ["Please enter amount to deposit"]
        if not amount.isnumeric():
            return ['Please enter a valid amount']
        amount = float(amount)
        if amount < 1:
            return ['Amount should be greater than 0']
        return []

    @classmethod
    def validate_first_name(cls, first_name):
        if not first_name:
            return ["Please enter first name"]
        return []

    @classmethod
    def validate_last_name(cls, last_name):
        if not last_name:
            return ["Please enter first name"]
        return []

    @classmethod
    def validate_mobile(cls, mobile):
        if not mobile:
            return ["Please enter mobile"]
        return []

    @classmethod
    def validate_address(cls, address):
        if not address:
            return ["Please enter address"]
        return []

    @classmethod
    def validate_country(cls, country):
        if not country:
            return ["Please select a country"]
        return []

    @classmethod
    def validate_email(cls, email):
        if not email:
            return ["Email cannot be empty"]
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if not re.search(regex, email):
            return ["Please enter a valid email"]
        cursor = connection.cursor()
        user = cursor.execute("SELECT id  FROM user_credential where email =" + "'" + email + "'")
        if user:
            return ["Email has already taken"]
        return []

    @classmethod
    def validate_password(cls, pass1, pass2):
        if not pass1 or not pass2:
            return ["Please enter both password and retype password"]
        if pass1 != pass2:
            return ["Both password and retype password do not match"]
        return []

    @classmethod
    def validate_currency(cls, currency):
        if not currency:
            return ["Please select a currency"]
        return []
