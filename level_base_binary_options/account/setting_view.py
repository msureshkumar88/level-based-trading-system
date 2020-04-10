from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from utilities.helper import Helper
from utilities.user_helper import UserHelper

from guest.models import UserById
from guest.models import UserCredential

from django.db import connection


def settings(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')

    ac = Authentication(request)
    user_id = ac.get_user_session()

    if request.method == "POST":
        action = request.POST['action']
        if action == "Update":
            update_settings(request, user_id)
        if action == "Change password":
            update_password(request, user_id)
        if action == "Deposit":
            deposit(request, user_id)

    user_data = Helper.get_user_by_id(user_id)
    data = dict()
    data['user_data'] = user_data
    data['countries'] = Helper.get_countries()

    return render(request, 'settings.html', data)


def update_settings(request, user_id):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    mobile = request.POST['mobile']
    address = request.POST['address']
    country = request.POST['country']

    error_messages = []
    error_messages.extend(UserHelper.validate_first_name(first_name))
    error_messages.extend(UserHelper.validate_last_name(last_name))
    error_messages.extend(UserHelper.validate_mobile(mobile))
    error_messages.extend(UserHelper.validate_address(address))
    error_messages.extend(UserHelper.validate_country(country))

    if error_messages:
        return error_messages
    user_settings = UserById(id=user_id, fname=first_name, lname=last_name, mobile=mobile, country=country,
                             address=address)
    user_settings.update()


def update_password(request, user_id):
    crrpassword = request.POST['crrpassword']
    password = request.POST['password']
    repassword = request.POST['repassword']
    error_message = []
    user_data = Helper.get_user_by_id(user_id)

    error_message.extend(validate_current_password(crrpassword, user_data['email']))
    error_message.extend(validate_new_password(password, repassword))
    print(error_message)
    if error_message:
        return error_message

    new_pass = Helper.password_encrypt(password)
    q = UserCredential(email=user_data['email'], password=new_pass)
    q.update()


def deposit(request, user_id):
    amount = request.POST['vcurrency']
    error_messages = []
    error_messages.extend(UserHelper.validate_amount(amount))
    if error_messages:
        return error_messages

    user_data = Helper.get_user_by_id(user_id)
    amount = float(amount)
    balance = user_data['vcurrency'] + amount
    user_settings = UserById(id=user_id, vcurrency=balance)
    user_settings.update()
    pass


def validate_current_password(password, email):
    if not password:
        return ["Current password cannot be empty"]
    password = Helper.password_encrypt(password)

    q = f"SELECT * FROM user_credential WHERE email = '{email}'"
    cursor = connection.cursor()
    result = cursor.execute(q)
    if result[0]['password'] != password:
        return ["Current password is invalid please reenter"]
    return []


def validate_new_password(pass1, pass2):
    if not pass1 and not pass2:
        return ["Please enter both new password and retype password"]
    if not pass1:
        return ["Please enter new password"]
    if not pass2:
        return ["please retype password"]
    if pass1 != pass2:
        return ["new and retype password do not match"]
    return []
