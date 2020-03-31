from django.shortcuts import render, redirect
from utilities.authentication import Authentication

# Create your views here.

def account(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    return render(request, 'account.html')

