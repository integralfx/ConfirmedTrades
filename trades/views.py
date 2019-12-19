from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404

from .models import Redditor, Trade

class TradeListView(ListView):
    model = Trade
    context_object_name = 'trades'
    template_name = 'trades/home.html'
    paginate_by = 20
    ordering = ['user1']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    def get_queryset(self):
        if 'q' in self.request.GET:
            q = self.request.GET['q']
            return Trade.objects.filter(user1__username__icontains=q).order_by('user2')
        else:
            return super().get_queryset()


def trades(req, username):
    redditor = get_object_or_404(Redditor, username=username)
    trades = Trade.objects.filter(user1=redditor).order_by('user2')
    return render(req, 'trades/trades.html', { 'redditor': redditor, 'trades': trades })

