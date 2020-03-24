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
    return render(request, 'register.html')