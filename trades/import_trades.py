from trades.models import Redditor, Trade
from os import listdir
import os.path
from tqdm import tqdm

def import_trades():
    files = listdir('trades/comment_urls')
    total = 212282 - 45000 + 1
    with tqdm(total=total, unit='trades') as pbar:
        for file in files:
            with open(f'trades/comment_urls/{file}') as f:
                for url in f.readlines():
                    tokens = url.split(':')
                    id = int(tokens[0])
                    comment_url = tokens[1][1:]

                    trade = Trade.objects.get(id=id)
                    trade.comment_url = comment_url
                    trade.save()

                    pbar.set_postfix(id=id)
                    pbar.update()