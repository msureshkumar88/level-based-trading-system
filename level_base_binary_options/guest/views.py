from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from django.http import HttpResponse

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
        print(username)
    return render(request, 'register.html')