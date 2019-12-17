from django.views.generic import ListView
from django.shortcuts import render

from .models import Redditor, Trade

class TradeListView(ListView):
    model = Trade
    context_object_name = 'trades'
    template_name = 'trades/home.html'
    paginate_by = 20

    