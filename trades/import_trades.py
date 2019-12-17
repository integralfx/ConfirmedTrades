from trades.models import Redditor, Trade

def find_username2(trades, username1, comment_id):
    for username2, comment_ids in trades.items():
        if username1 != username2 and comment_id in comment_ids:
            return username2
    return None


with open("C:\\Users\\Jordan\\Desktop\\Projects\\DjangoConfirmedTrades\\confirmedtrades\\trades\\confirmed_trades.txt", 'r') as file:
    trades = {}
    for line in file:
        if line == '':
            continue
        username, rest = line.split(':')
        comment_ids = rest.split(',')
        for i in range(len(comment_ids)):
            comment_ids[i] = comment_ids[i].strip()
        trades[username] = comment_ids
    # Insert usernames
    #for username in trades.keys():
    #    Redditor.objects.get_or_create(username=username)

    # Insert trades
    for username, comment_ids in trades.items():
        print(username)
        user1 = Redditor.objects.get(username=username)
        for id in comment_ids:
            username2 = find_username2(trades, username, id)
            user2 = Redditor.objects.get(username=username2)
            Trade.objects.create(user1=user1, user2=user2, comment_id=id)
            print(f'\tAdded trade {id} with {username2}')
