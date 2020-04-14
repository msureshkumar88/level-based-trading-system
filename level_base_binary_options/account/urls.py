from django.urls import path

from . import views
from . import level_based_view
from . import setting_view
from . import statements_view
from . import search_level_based_view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('account', views.account, name='account'),
    path('account/levels', level_based_view.levels, name='levels'),
    path('account/search_trades', search_level_based_view.level_based_search, name='search'),
    path('account/statements', statements_view.statements, name='statements'),
    path('account/settings', setting_view.settings, name='settings'),
    path('account/charts', views.charts, name='charts'),
    path('account/logout', views.logout, name='logout'),
]

