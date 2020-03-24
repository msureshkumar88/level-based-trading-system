from django.shortcuts import render

from django.http import HttpResponse

# Create your views here.

def home(request):

    return render(request, 'home.html')


def login(request):

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']
        print(email,password)

    return render(request, 'login.html')

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