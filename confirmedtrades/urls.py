from django.contrib import admin
from django.urls import path

from trades import views

urlpatterns = [
    path('', views.TradeListView.as_view(), name='home'),
    path('trades/<username>/', views.trades, name='trades'),
    path('admin/', admin.site.urls),
]
