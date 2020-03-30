from django.shortcuts import render, redirect
from utilities.authentication import Authentication
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
    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']
        request.session['email'] = email

        # ac.save_user_session(email)
        # print(ac.get_user_session())

        temp_email = "sam@gmail.com"
        temp_pass = "123"
        if ac.is_user_logged_in():
            return redirect('/account')

        if email == temp_email and password == temp_pass:
            ac.save_user_session(email)

        else:
            data['message'] = "User does not exists"

        # del request.session['user_session']
        # print(ac.get_user_session())
        # print(request.session['email'])
        # print(email,password)

    return render(request, 'login.html', data)

def register(request):
    if request.method == "POST":
        username = request.POST['username']
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

        # TODO - add validations

        # insert = User(email = email, address = address, password = password, country = country,currency = currency, fname = first_name,lname =last_name, mobile = mobile, username = username,  vcurrency = virtual_currency)
        # insert.save()


        # user_id = ""
        # try:
        #     q = UserCredential.objects.filter(email=email)
        #     user_id = q.get().id
        # except:
        #     print("An exception occurred")
        cursor = connection.cursor()
        user = cursor.execute("SELECT id  FROM user_credential where email =" + "'" + email + "'")
        # check whether email exists
        if not user:
            # create user credentials
            insert = UserCredential(email=email, password=password, username=username)
            insert.save()

            # get newly created user id
            user_id = UserCredential.objects.filter(email=email)
            user_id = user_id.get().id

            # save user general details
            new_user = UserById(id = user_id, address = address, country = country,currency = currency, fname = first_name,lname =last_name, mobile = mobile, vcurrency = virtual_currency)
            new_user.save()
            
    return render(request, 'register.html')