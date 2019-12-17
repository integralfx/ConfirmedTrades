from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404

from .models import Redditor, Trade

class TradeListView(ListView):
    model = Trade
    context_object_name = 'trades'
    template_name = 'trades/home.html'
    paginate_by = 20
    ordering = ['user1']


def trades(req, redditor_id):
    redditor = get_object_or_404(Redditor, id=redditor_id)
    trades = Trade.objects.filter(user1=redditor)
    return render(req, 'trades/trades.html', { 'redditor': redditor, 'trades': trades })