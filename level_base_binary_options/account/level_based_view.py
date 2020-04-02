from django.shortcuts import render, redirect
from utilities.authentication import Authentication

from django.db import connection
from datetime import datetime
from datetime import timedelta

from utilities.helper import Helper
from .models import UserTransactionsBinary
from .models import TransactionsByStatusBinary


def levels(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    data = dict()
    if request.method == "POST":
        pass

    return render(request, 'level_based.html', data)
