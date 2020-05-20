from django.shortcuts import render, redirect
from utilities.authentication import Authentication


def view(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    data = dict()
    if not ac.is_user_logged_in():
        return redirect('/login')
    data['auth'] = ac.is_user_logged_in()
    return render(request, 'dashboard.html', data)
