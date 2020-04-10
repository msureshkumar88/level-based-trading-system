from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from utilities.helper import Helper
from utilities.user_helper import UserHelper

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
    # if ac.is_user_logged_in():
    #     return redirect('/account')
    # ac.logout()
    # if user is logged in redirect to account page
    if ac.is_user_logged_in():
        return redirect('/account')

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']

        # encrypt user enter password in the login page to check with db password
        password_encrypted = Helper.password_encrypt(password)

        cursor = connection.cursor()

        # check whether user exists in the DB
        user = cursor.execute("SELECT *  FROM user_credential where email =" + "'" + email + "' ")

        if not user:
            data['message'] = "User does not exists"

        if user and user[0]['password'] == Helper.password_encrypt(password):
            # get loged user details
            q = f"SELECT *  FROM user_by_id where id = {user[0]['id']}";
            user = cursor.execute(q)
            # print(user[0])

            # create user session and store user id
            ac.save_user_session(str(user[0]['id']))
            print(ac.get_user_session())
            return redirect('/account')

        data['message'] = "invalid password"

        # return render(request, 'login.html', data)
        # request.session['email'] = email

        # ac.save_user_session(email)
        # print(ac.get_user_session())

        # temp_email = "sam@gmail.com"
        # temp_pass = "123"
        # if ac.is_user_logged_in():
        #     return redirect('/account')
        #
        # if email == temp_email and password == temp_pass:
        #     ac.save_user_session(email)
        #
        # else:
        #     data['message'] = "User does not exists"

        # del request.session['user_session']
        # print(ac.get_user_session())
        # print(request.session['email'])
        # print(email,password)

    return render(request, 'login.html', data)


def register(request):
    ac = Authentication(request)
    if ac.is_user_logged_in():
        return redirect('/account')
    if request.method == "POST":
        create_user(request)
    data = dict()
    data['countries'] = Helper.get_countries()

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
    print(error_messages)
    if error_messages:
        return error_messages
    # return render(request, 'register.html')

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
