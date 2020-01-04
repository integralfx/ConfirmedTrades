from django.contrib import admin
from django.urls import path

from trades import views

urlpatterns = [
    path('', views.TradeListView.as_view(), name='home'),
    path('search/', views.RedditorListView.as_view(), name='search'),
    path('trades/users/', views.RedditorListView.as_view(), name='trades-users'),
    path('trades/users/<username>/', views.user_trades, name='user-trades'),
    path('trades/update', views.update, name='update'),
    path('admin/', admin.site.urls),
]
