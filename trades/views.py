from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Max, Q, F

from .forms import UpdateTradesForm
from .models import Redditor, Trade

class TradeListView(ListView):
    model = Trade
    context_object_name = 'trades'
    template_name = 'trades/all-trades.html'
    paginate_by = 20
    ordering = ['user1']

    def get_queryset(self):
        qs = Trade.objects.all()

        if 'sort-user1' in self.request.GET:
            sort_order = self.request.GET['sort-user1']
            qs = qs.order_by(f'{"-" if sort_order == "desc" else ""}user1__username')
        elif 'sort-user2' in self.request.GET:
            sort_order = self.request.GET['sort-user2']
            qs = qs.order_by(f'{"-" if sort_order == "desc" else ""}user2__username')
        elif 'sort-confirmation' in self.request.GET:
            sort_order = self.request.GET['sort-confirmation']
            qs = qs.order_by(f'{"-" if sort_order == "desc" else ""}comment_id')
        elif 'sort-date' in self.request.GET:
            sort_order = self.request.GET['sort-date']
            qs = qs.order_by(f'{"-" if sort_order == "desc" else ""}confirmation_datetime')

        return qs

class RedditorListView(ListView):
    model = Redditor
    context_object_name = 'redditors'
    template_name = 'trades/trades-users.html'
    paginate_by = 20
    ordering = ['username']

    def get_queryset(self):
        qs = Redditor.objects.all().annotate(last_confirmation_date=Max('trades1__confirmation_datetime'))

        if 'q' in self.request.GET:
            q = self.request.GET['q']
            qs = qs.filter(username__icontains=q)
        
        if 'sort-user' in self.request.GET:
            sort_order = self.request.GET['sort-user']
            qs = qs.order_by(f'{"-" if sort_order == "desc" else ""}username')
        elif 'sort-trades' in self.request.GET:
            sort_order = self.request.GET['sort-trades']
            qs = (qs.annotate(num_trades=Count('trades1'))
                    .order_by(f'{"-" if sort_order == "desc" else ""}num_trades'))
        elif 'sort-last' in self.request.GET:
            sort_order = self.request.GET['sort-last']
            qs = qs.order_by(f'{"-" if sort_order == "desc" else ""}last_confirmation_date')

        return qs


def user_trades(req, username):
    redditor = get_object_or_404(Redditor, username=username)
    trades = Trade.objects.filter(user1=redditor).order_by("user2__username")

    if 'sort-user' in req.GET:
        sort_order = req.GET['sort-user']
        trades = trades.order_by(f'{"-" if sort_order == "desc" else ""}user2__username')
    elif 'sort-confirmation' in req.GET:
        sort_order = req.GET['sort-confirmation']
        trades = trades.order_by(f'{"-" if sort_order == "desc" else ""}comment_id')
    elif 'sort-date' in req.GET:
        sort_order = req.GET['sort-date']
        trades = trades.order_by(f'{"-" if sort_order == "desc" else ""}confirmation_datetime')

    return render(req, 'trades/user-trades.html', { 'redditor': redditor, 'trades': trades })


def update(req):
    if req.method == 'POST':
        form = UpdateTradesForm(req.POST)
        if form.is_valid():
            return redirect('home')
    else:
        form = UpdateTradesForm()

    return render(req, 'trades/update.html', { 'form': form })