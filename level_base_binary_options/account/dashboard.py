from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from utilities.helper import Helper

def view(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    data = dict()
    if not ac.is_user_logged_in():
        return redirect('/login')

    user_id = ac.get_user_session()
    data['auth'] = ac.is_user_logged_in()
    data["pending_trades"] = Helper.get_latest_pending_trades(user_id)
    data["latest_outcomes"] = Helper.get_latest_outcome_trades(user_id)
    data["user_currency"] = Helper.get_user_by_id(user_id)['currency']
    return render(request, 'dashboard.html', data)

