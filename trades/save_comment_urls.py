from trades.models import Redditor, Trade
from tqdm import tqdm

def save_comment_urls(start_id, count=1000):
    trades = Trade.objects.filter(id__gte=start_id)[:count]
    with open(f'url_{start_id}-{start_id + count - 1}.txt', 'w') as file:
        with tqdm(total=trades.count(), unit='trades') as pbar:
            for trade in trades:
                comment_url = trade.get_comment_url()
                file.write(f'{trade.id}: {comment_url}\n')
                pbar.set_postfix(comment_id=trade.comment_id)
                pbar.update()