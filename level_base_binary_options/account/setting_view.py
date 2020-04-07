from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from utilities.helper import Helper

from guest.models import UserById


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
    error_messages.extend(validate_first_name(first_name))
    error_messages.extend(validate_last_name(last_name))
    error_messages.extend(validate_mobile(mobile))
    error_messages.extend(validate_address(address))
    error_messages.extend(validate_country(country))

    if error_messages:
        return error_messages
    user_settings = UserById(id=user_id, fname=first_name, lname=last_name, mobile=mobile, country=country,
                             address=address)
    user_settings.update()


def validate_first_name(first_name):
    if not first_name:
        return ["Please enter first name"]
    return []


def validate_last_name(last_name):
    if not last_name:
        return ["Please enter first name"]
    return []


def validate_mobile(mobile):
    if not mobile:
        return ["Please enter mobile"]
    return []


def validate_address(address):
    if not address:
        return ["Please enter mobile"]
    return []


def validate_country(country):
    if not country:
        return ["Please enter mobile"]
    return []
