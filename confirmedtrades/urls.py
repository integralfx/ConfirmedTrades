from django.contrib import admin
from django.urls import path

from trades import views

urlpatterns = [
    path('', views.RedditorListView.as_view(), name='home'),
    path('search', views.RedditorListView.as_view(), name='search'),
    path('trades/<username>/', views.trades, name='trades'),
    path('admin/', admin.site.urls),
]
