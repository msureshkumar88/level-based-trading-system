from django.urls import path

from . import views
from . import level_based_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('account', views.account, name='account'),
    path('account/levels', level_based_view.levels, name='levels'),
    path('account/search_trades', views.search, name='search'),
    path('account/statements', views.statements, name='statements'),
    path('account/settings', views.settings, name='settings'),
]

