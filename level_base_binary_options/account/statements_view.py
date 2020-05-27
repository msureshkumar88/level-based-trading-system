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

# import findspark
# import pyspark
# findspark.init("C:\spark-2.4.0-bin-hadoop2.7\\")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plotly.offline import plot
import plotly.graph_objs as go


#  TODO: fix filtering not functioning issue
def statements(request):
    ac = Authentication(request)
    # if user is not logged in redirect to login page
    if not ac.is_user_logged_in():
        return redirect('/login')
    # print(list(map(str, Status)))
    data = dict()
    user_id = ac.get_user_session()
    user_data = Helper.get_user_by_id(user_id)
    data['user_data'] = user_data
    if request.method == "POST":
        data['results'] = search(request)

    status = []
    outcome = []
    [outcome.append(e.value) for e in Outcome]
    [status.append(e.value) for e in Status]
    data["trading_status"] = status
    data["trading_outcome"] = outcome
    data['today_date'] = datetime.now().strftime("%Y-%m-%d")
    data['auth'] = ac.is_user_logged_in()

    # query = f"SELECT * from transactions_by_state where status in {tuple(status)}"
    # print(query)
    # cursor = connection.cursor()
    # results = cursor.execute(query)
    # print(results)

    # spark - pyspark
    # val = sc.textFile("C:\\Users\\suresh\\AppData\\Local\\Programs\\Python\\Python37\\LICENSE.txt").collect()
    # print(len(val))
    # data1 = ["pandas", "i like pandas"]
    # sc = pyspark.SparkContext.getOrCreate()
    # lines = sc.parallelize(data1)
    # aa = lines.collect()
    # print(aa)

    # pandas

    # s = pd.Series([1, 3, 5, np.nan, 6, 8])
    # print(s)
    # ts = pd.Series(np.random.randn(1000), index = pd.date_range('1/1/2000', periods=1000))
    # ts = ts.cumsum()
    #
    # # img = ts.savefig('myfig')
    # plt.plot([1, 2, 3,4])
    # img = plt.savefig('myfig')
    # # ts.plot()
    # data['cc'] = img
    #
    # fig = go.Figure()
    # scatter = go.Scatter(x=[0, 1, 2, 3], y=[0, 1, 2, 3],
    #                      mode='lines', name='test',
    #                      opacity=0.8, marker_color='green')
    # fig.add_trace(scatter)
    # plt_div = plot(fig, output_type='div')
    # data['plt_div'] = plt_div
    return render(request, 'statements.html', data)


def search(request):
    status = request.POST['status']
    outcome = request.POST['outcome']
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    min_amount = request.POST['min_amount']
    max_amount = request.POST['max_amount']

    error_messages = []
    error_messages.extend(search_all_inputs(request))

    print(error_messages)
    if error_messages:
        return error_messages
    ac = Authentication(request)
    user_id = ac.get_user_session()

    cursor = connection.cursor()
    # initial_query = f"SELECT * FROM transactions_by_state WHERE user_id = {user_id} "
    # if status:
    #     initial_query = initial_query + filter_where_status(status)
    #  TODO: fix filtering for following parameters
    # if not status:
    #     initial_query = initial_query + filter_where_status_in()
    #
    # if outcome:
    #     initial_query = initial_query + filter_where_outcome(outcome)
    #
    # if not outcome:
    #     initial_query = initial_query + filer_where_outcome_in()
    #
    #
    # if not start_date and not end_date and not min_amount and not max_amount:
    #     initial_query = initial_query + filter_date_amount_none()
    #
    # if start_date or min_amount:
    #     initial_query = initial_query + filter_greater_para(start_date, min_amount)
    #
    # if end_date or max_amount:
    #     initial_query = initial_query + filter_less_para(end_date, max_amount)

    # print(initial_query)
    # results = cursor.execute(initial_query)

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
        df = df.loc[df['amount'] >= min_amount]

    if max_amount:
        df = df.loc[df['amount'] <= max_amount]

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


# https://www.datastax.com/blog/2015/06/deep-look-cql-where-clause
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

# TODO: search not working properly fix it
