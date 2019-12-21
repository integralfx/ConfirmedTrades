from trades.models import Redditor, Trade
from os import listdir
import os.path
from tqdm import tqdm
from trades.ConfirmedTrades import ConfirmedTrades
from trades.reddit import reddit

def import_trades():
    files = listdir('trades/comment_urls')
    total = 212282 - 45000 + 1
    with tqdm(total=total, unit='trades') as pbar:
        for file in files:
            with open(f'trades/comment_urls/{file}') as f:
                for url in f.readlines():
                    tokens = url.split(':')
                    id = int(tokens[0])
                    comment_url = tokens[1][1:] + ':' + tokens[2]

                    trade = Trade.objects.get(id=id)
                    trade.comment_url = comment_url
                    trade.save()

                    pbar.set_postfix(id=id)
                    pbar.update()


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


ct = ConfirmedTrades(reddit)
ct.parse_urls('trades/confirmed_trades_urls.txt')

def get_confirmed_trades(url_index):
    url = ct.urls[url_index]
    trades = ct.get_trades_from_url(url)

    # Split url into submission id and title
    tokens = url.split('/')[6:8]
    filename = f'{tokens[0]}-{tokens[1]}.txt'
    with open(filename, 'w') as file:
        for name, comment_ids in trades.items():
            for i in range(len(comment_ids)):
                comment_ids[i] = comment_ids[i].strip()

            file.write(f'{name}: {", ".join(comment_ids)}\n')


# Find the other user that traded with user1.
def find_user2(trades, user1, comment_id):
    for user, comment_ids in trades.items():
        for cid in comment_ids:
            if user != user1 and cid == comment_id:
                return user

    return None


def import_confirmed_trades():
    files = listdir('trades/confirmed_trades')
    trades = {}
    for file in files:
        with open(f'trades/confirmed_trades/{file}') as f:
            for trade in f.readlines():
                tokens = trade.split(':')
                user = tokens[0]
                comment_ids = [c.strip() for c in tokens[1].split(',')]

                if user in trades:
                    trades[user].extend(comment_ids)
                else:
                    trades[user] = comment_ids

    for user, _ in tqdm(trades.items(), desc='Adding new Redditors', unit='users'):
        if not Redditor.objects.filter(username=user).exists():
            Redditor.objects.create(username=user)

    total = sum(list(map(lambda comment_ids: len(comment_ids), trades.values())))

    with tqdm(desc='Adding new Trades', total=total, unit='trades') as pbar:
        for user, comment_ids in trades.items():
            user1 = Redditor.objects.get(username=user)
            for cid in comment_ids:
                pbar.set_postfix(comment_id=cid)
                username2 = find_user2(trades, user, cid)
                if username2:
                    user2 = Redditor.objects.get(username=username2)
                    if not Trade.objects.filter(user1=user1, user2=user2, comment_id=cid).exists():
                        url = ct.get_url_from_comment_id(cid)
                        Trade.objects.create(user1=user1, user2=user2, comment_id=cid, comment_url=url)

                pbar.update()


def update_confirmed_trades(url):
    trades = ct.get_trades_from_url(url)

    with tqdm(desc='Adding new users', total=len(trades), unit='users') as pbar:
        for user in trades:
            pbar.set_postfix(user=user)
            if not Redditor.objects.filter(username=user).exists():
                Redditor.objects.create(username=user)
            pbar.update()

    total = sum(list(map(lambda ids: len(ids), trades.values())))
    with tqdm(desc='Adding new trades', total=total, unit='trades') as pbar:
        for username1, comment_ids in trades.items():
            user1 = Redditor.objects.get(username=username1)
            for cid in comment_ids:
                username2 = find_user2(trades, username1, cid)
                user2 = Redditor.objects.get(username=username2)
                url = ct.get_url_from_comment_id(cid)
                Trade.objects.create(user1=user1, user2=user2, comment_id=cid, comment_url=url)
                pbar.update()
