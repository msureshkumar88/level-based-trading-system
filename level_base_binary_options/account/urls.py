from django.urls import path

from . import views
from . import level_based_view
from . import setting_view
from . import statements_view
from . import search_level_based_view
from . import restapi
from . import analysis
from . import dashboard

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('account', dashboard.view, name='dashboard'),
    path('account/binary', views.account, name='binary'),
    path('account/save_binary', views.create_trade, name='binary_save'),
    path('account/levels', level_based_view.levels, name='levels'),
    path('account/save_levels', level_based_view.create_trade, name='levels_save'),
    path('account/search_trades', search_level_based_view.level_based_search, name='search'),
    path('account/statements', statements_view.statements, name='statements'),
    path('account/settings', setting_view.settings, name='settings'),
    path('account/charts', analysis.chart_view, name='charts'),
    path('account/charts-get', analysis.chart, name='charts'),
    path('account/logout', views.logout, name='logout'),
    path('account/get-transaction', restapi.get_transaction, name='get_transaction'),
    path('account/get-chart-data', restapi.get_chart_data, name='get_chart_data'),
    path('account/get-pending-order', restapi.get_pending_order, name='get_pending_order'),
    path('account/join-trade', search_level_based_view.join_trade, name='join_trade'),
]

