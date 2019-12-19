import praw
import re
from collections import OrderedDict
from tqdm import tqdm

class ConfirmedTrades:
    def __init__(self, reddit):
        self.reddit = reddit
        self.trades = {}
        self.urls = []

    # returns {<username>:[<comment_ids>]} where:
    #   username is the Reddit username
    #   comment_ids are a list of the parent_ids of a confirmed trade
    def get_trades_from_url(self, url):
        submission = self.reddit.submission(url=url)
        submission.comment_sort = 'new'
        submission.comments.replace_more(limit=None)
        confirmed_trades = {}

        for top_level_comment in submission.comments:
            if top_level_comment.author is None:
                continue

            # usernames are not case sensitive
            top_level_user = top_level_comment.author.name.lower()

            # find the mentioned user
            match = re.search('u/\w+', top_level_comment.body)
            if match is None:
                continue
            mentioned_user = match.group().lower()[2:]

            for second_level_comment in top_level_comment.replies:
                if second_level_comment.author is None:
                    continue

                second_level_user = second_level_comment.author.name.lower()

                if second_level_user != mentioned_user:
                    pbar.update()
                    continue

                if 'confirmed' in second_level_comment.body.lower():
                    if top_level_user not in confirmed_trades:
                        confirmed_trades[top_level_user] = [top_level_comment.id]
                    else:
                        if top_level_comment.id not in confirmed_trades[top_level_user]:
                            confirmed_trades[top_level_user].append(top_level_comment.id)

                    if second_level_user not in confirmed_trades:
                        confirmed_trades[second_level_user] = [top_level_comment.id]
                    else:
                        if top_level_comment.id not in confirmed_trades[second_level_user]:
                            confirmed_trades[second_level_user].append(top_level_comment.id)

                    break

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

