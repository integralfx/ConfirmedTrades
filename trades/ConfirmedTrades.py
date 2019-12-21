import praw
import re
from collections import OrderedDict
from tqdm import tqdm

class ConfirmedTrades:
    def __init__(self, reddit):
        self.reddit = reddit
        self.trades = {}
        self.urls = []


    # Checks if mentioned_user replied 'confirmed' and returns the parent comment id.
    # TODO: Account for confirmations of other users. e.g. A traded with B, B confirmed, B traded with C, C confirmed.
    def get_mentioned_user_confirmed_id(self, parent_comment_id, comment, mentioned_user):
        if comment.author is None:
            return None

        if mentioned_user:
            user = comment.author.name.lower()
            if user == mentioned_user and 'confirmed' in comment.body.lower():
                return parent_comment_id

        match = re.search('u/[A-Za-z0-9_-]+', comment.body)
        if match:
            mentioned_user = match.group().lower()[2:]

        for reply in comment.replies:
            confirmed_id = self.get_mentioned_user_confirmed_id(comment.id, reply, mentioned_user)
            if confirmed_id:
                return confirmed_id

        return None


    # returns {<username>:[<comment_ids>]} where:
    #   username is the Reddit username
    #   comment_ids are a list of the parent_ids of a confirmed trade
    # Assumes that each trade is in a different top level comment.
    def get_trades_from_url(self, url):
        submission = self.reddit.submission(url=url)
        submission.comment_sort = 'new'
        submission.comments.replace_more(limit=None)
        confirmed_trades = {}

        def add_confirmed_trade(user, comment_id):
            if user not in confirmed_trades:
                confirmed_trades[user] = [comment_id]
            else:
                if comment_id not in confirmed_trades[user]:
                    confirmed_trades[user].append(comment_id)

        for comment in submission.comments:
            if comment.author is None:
                continue

            # usernames are not case sensitive
            top_level_user = comment.author.name.lower()

            # find the mentioned user
            match = re.search('u/[A-Za-z0-9_-]+', comment.body)
            if match is None:
                continue
            mentioned_user = match.group().lower()[2:]

            for reply in comment.replies:
                confirmation_id = self.get_mentioned_user_confirmed_id(comment.id, reply, mentioned_user)
                if confirmation_id:
                    add_confirmed_trade(top_level_user, confirmation_id)
                    add_confirmed_trade(mentioned_user, confirmation_id)

        return confirmed_trades
        


    # returns a list of the urls of the monthly confirmed trade threads
    def get_submission_urls(self):
        urls = []
        hws = self.reddit.subreddit('hardwareswap')
        for submission in hws.search(query='author:hwsbot confirmed trade thread', sort='new'):
            urls.append(submission.url)

        return urls

    def get_url_from_comment_id(self, comment_id):
        comment = self.reddit.comment(comment_id)
        return 'https://www.reddit.com' + comment.permalink

    def parse_trades(self, filename):
        self.trades.clear()

        with open(filename, 'r') as file:
            for line in file:
                if line == '':
                    continue
                username, rest = line.split(':')
                comment_ids = rest.split(',')
                for i in range(len(comment_ids)):
                    comment_ids[i] = comment_ids[i].strip()

                self.trades[username] = comment_ids

    def save_trades(self, filename):
        if not self.trades:
            return False

        with open(filename, 'w') as file:
            for name, comment_ids in self.trades.items():
                for i in range(len(comment_ids)):
                    comment_ids[i] = comment_ids[i].strip()

                file.write(f'{name}: {", ".join(comment_ids)}\n')

            return True

    def sort_trades(self):
        for user in self.trades:
            self.trades[user].sort()
        self.trades = OrderedDict(sorted(self.trades.items()))

    def merge_trades(self, trades):
        for user in trades:
            # user found, so add ids that aren't already in the list
            if user in self.trades:
                for id in trades[user]:
                    if id not in self.trades[user]:
                        self.trades[user].append(id)
            # user not found, so add it
            else:
                self.trades[user] = trades[user]

    def update_trades_from_url(self, url):
        self.merge_trades(self.get_trades_from_url(url))

    # returns a list of comment ids of the confirmed trades
    # between user1 and user2
    def get_trades_between(self, user1, user2):
        if user1.lower() not in self.trades or \
           user2.lower() not in self.trades:
            return []

        ids1 = set(self.trades[user1.lower()])
        ids2 = set(self.trades[user2.lower()])

        return list(ids1.intersection(ids2))

    def parse_urls(self, filename):
        with open(filename, 'r') as file:
            # last element is a blank line
            self.urls = file.read().split('\n')[:-1]

    def save_urls(self, filename):
        if not self.urls:
            return False

        with open(filename, 'w') as file:
            for url in self.urls:
                file.write(f'{url}\n')

