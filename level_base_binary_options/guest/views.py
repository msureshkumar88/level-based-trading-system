from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from utilities.helper import Helper
from utilities.user_helper import UserHelper
from utilities.state_keys import StatKeys

from datetime import datetime

from .models import UserById
from .models import UserCredential
from django.http import HttpResponse

from django.db import connection


# Create your views here.

def home(request):
    return render(request, 'home.html')


def login(request):
    data = {}
    ac = Authentication(request)
    # if user is logged in redirect to account page
    if ac.is_user_logged_in():
        return redirect('/account')

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']

        error_messages = validate_login_inputs(email, password)
        if not error_messages:
            # encrypt user enter password in the login page to check with db password
            password_encrypted = Helper.password_encrypt(password)

            cursor = connection.cursor()

            # check whether user exists in the DB
            user = cursor.execute("SELECT *  FROM user_credential where email =" + "'" + email + "' ")

            if user and user[0]['password'] == Helper.password_encrypt(password):
                # get loged user details
                q = f"SELECT *  FROM user_by_id where id = {user[0]['id']}";
                user = cursor.execute(q)

                # create user session and store user id
                ac.save_user_session(str(user[0]['id']))
                return redirect('/account')

            error_messages.append("Invalid email or password")
        data["error_messages"] = error_messages

    return render(request, 'login.html', data)


def validate_login_inputs(email, password):
    error_messages = []
    error_messages.extend(UserHelper.validate_guest_email(email))
    error_messages.extend(UserHelper.validate_guest_password(password))
    if error_messages:
        return error_messages
    return []


def register(request):
    ac = Authentication(request)
    if ac.is_user_logged_in():
        return redirect('/account')
    error_messages = []
    data = dict()
    if request.method == "POST":
        error_messages = create_user(request)
        if error_messages:
            data["post_data"] = request.POST
        else:
            data["success"] = True

    data['countries'] = Helper.get_countries()
    data['currency'] = Helper.get_currency()
    data['error_messages'] = error_messages
    return render(request, 'register.html', data)


def create_user(request):
    email = request.POST['email']
    password = request.POST['password']
    repassword = request.POST['repassword']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    mobile = request.POST['mobile']
    address = request.POST['address']
    country = request.POST['country']
    currency = request.POST['currency']
    virtual_currency = request.POST['virtual_currency']
    error_messages = []

    error_messages.extend(UserHelper.validate_email(email))
    error_messages.extend(UserHelper.validate_password(password, repassword))
    error_messages.extend(UserHelper.validate_first_name(first_name))
    error_messages.extend(UserHelper.validate_last_name(last_name))
    error_messages.extend(UserHelper.validate_mobile(mobile))
    error_messages.extend(UserHelper.validate_address(address))
    error_messages.extend(UserHelper.validate_country(country))
    error_messages.extend(UserHelper.validate_currency(currency))
    error_messages.extend(UserHelper.validate_amount(virtual_currency))
    if error_messages:
        return error_messages

    cursor = connection.cursor()
    user = cursor.execute("SELECT id  FROM user_credential where email =" + "'" + email + "'")
    # check whether email exists
    if not user:
        # create user credentials
        insert = UserCredential(email=email, password=Helper.password_encrypt(password))
        insert.save()

        # get newly created user id
        user_id = UserCredential.objects.filter(email=email)
        user_id = user_id.get().id

        # save user general details
        new_user = UserById(id=user_id, email=email, address=address, country=country, currency=currency,
                            fname=first_name, lname=last_name, mobile=mobile, vcurrency=virtual_currency,
                            created_date=datetime.now())
        new_user.save()

        Helper.store_state_value(user_id, StatKeys.BALANCE.value, virtual_currency, 'subtract')
