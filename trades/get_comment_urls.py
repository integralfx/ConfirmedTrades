from trades.models import Redditor, Trade
from tqdm import tqdm

trades = Trade.objects.filter(comment_url='https://reddit.com/')
total = Trade.objects.count() - trades[0].id

# TODO: Use bulk_update()
with tqdm(total=total, unit='trades') as pbar:
    for trade in trades:
        trade.comment_url = trade.get_comment_url()
        trade.save()
        pbar.set_postfix(comment_id=trade.comment_id)
        pbar.update()