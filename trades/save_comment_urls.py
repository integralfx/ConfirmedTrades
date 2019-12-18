from trades.models import Redditor, Trade
from tqdm import tqdm
import os.path

def save_comment_urls(start_id, count=1000):
    trades = Trade.objects.filter(id__gte=start_id)[:count]
    filename = f'trades/comment_urls/url_{start_id}-{start_id + count - 1}.txt'

    if os.path.isfile(filename):
        print(f'{filename} already exists')
        return

    with open(filename, 'w') as file:
        with tqdm(total=trades.count(), unit='trades') as pbar:
            for trade in trades:
                comment_url = trade.get_comment_url()
                file.write(f'{trade.id}: {comment_url}\n')
                pbar.set_postfix(comment_id=trade.comment_id)
                pbar.update()


def merge_urls(start, end, step):
    url_files = [f'trades/comment_urls/url_{i}-{i + step - 1}.txt' for i in range(start, end, step)]

    urls = []
    for url_file in url_files:
        with open(url_file) as file:
            lines = file.readlines()
            urls.extend(lines)
            file.close()

    with open(f'trades/comment_urls/url_{start}-{end - 1}.txt', 'w') as file:
        file.writelines(urls)