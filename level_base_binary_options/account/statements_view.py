from django.shortcuts import render, redirect
from utilities.authentication import Authentication
from datetime import datetime
from datetime import timedelta

from utilities.trade_status import Status
from utilities.trade_outcome import Outcome

from utilities.helper import Helper
from utilities.trading import Trading

from django.db import connection

import pandas as pd

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plotly.offline import plot
import plotly.graph_objs as go



def statements(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    data = dict()
    user_id = ac.get_user_session()
    user_data = Helper.get_user_by_id(user_id)
    data['user_data'] = user_data
    if request.method == "POST":
        data['results'] = search(request)

    if request.method == "GET":
        data['results'] = get_initial_list(user_id)
    status = []
    outcome = []
    [outcome.append(e.value) for e in Outcome]
    [status.append(e.value) for e in Status]
    data["trading_status"] = status
    data["trading_outcome"] = outcome
    data['today_date'] = datetime.now().strftime("%Y-%m-%d")
    data['auth'] = ac.is_user_logged_in()
    data['current_user'] = user_id
    return render(request, 'statements.html', data)


def get_initial_list(user_id):
    cursor = connection.cursor()
    results = cursor.execute(f"select * from transactions_by_state WHERE user_id = {user_id}")
    if not results:
        return []
    df = pd.DataFrame(results)
    df = df.sort_values(by='created_date', ascending=False)
    return df.head(5).iterrows()


def search(request):
    status = request.POST['status']
    outcome = request.POST['outcome']
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    min_amount = request.POST['min_amount']
    max_amount = request.POST['max_amount']

    error_messages = []
    error_messages.extend(search_all_inputs(request))
    ac = Authentication(request)
    user_id = ac.get_user_session()

    cursor = connection.cursor()

    results = cursor.execute(f"select * from transactions_by_state WHERE user_id = {user_id}")
    if not results:
        return []

    if min_amount and max_amount:
        min_amount = float(min_amount)
        max_amount = float(max_amount)

    df = pd.DataFrame(results)
    if status:
        df = df.loc[df['status'] == status]

    if outcome:
        df = df.loc[df['outcome'] == outcome]

    if min_amount:
        df = df.loc[df['amount'] >= float(min_amount)]

    if max_amount:
        df = df.loc[df['amount'] <= float(max_amount)]

    if start_date:
        df = df.loc[df['created_date'] >= start_date]

    if end_date:
        df = df.loc[df['created_date'] <= end_date]

    return df.iterrows()


def search_all_inputs(request):
    for filed in request.POST:
        if filed != 'csrfmiddlewaretoken' and request.POST[filed]:
            return []
    return ["Nothing to search or filter "]


def get_status_list():
    status = []
    [status.append(e.value) for e in Status]
    return status


def get_outcome_list():
    outcome = []
    [outcome.append(e.value) for e in Outcome]
    return outcome


def filter_where_status(status):
    return f"AND status = '{status}' "


def filter_where_status_in():
    return f"AND status in {tuple(get_status_list())} "


def filter_where_outcome(outcome):
    return f"AND outcome = '{outcome}' "


def filer_where_outcome_in():
    return f"AND outcome in {tuple(get_outcome_list())} "


def filter_greater_para(start_date, min_amount):
    if not min_amount:
        min_amount = 0
    if not start_date:
        start_date = datetime.now().strftime('%Y-%m-%d')
    return f"AND (created_date,amount) >= ('{start_date}', {min_amount}) "


def filter_less_para(end_date, max_amount):
    if not max_amount:
        max_amount = 1000000000
    if not end_date:
        end_date = datetime.now() + timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')
    return f"AND (created_date,amount) <= ('{end_date}', {max_amount}) "


def filter_date_amount_none():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"AND (created_date,amount) >= ('{today}', {0}) AND (created_date,amount) <= ('{today}', {1000000000}) "


