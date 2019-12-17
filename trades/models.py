from django.db import models

import praw

def parse_praw_file():
    with open('trades/praw.txt', 'r') as file:
        lines = file.read().split('\n')
        return praw.Reddit(client_id=lines[0], client_secret=lines[1], user_agent=lines[2])

reddit = parse_praw_file()

class Redditor(models.Model):
    username = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.username


class Trade(models.Model):
    user1 = models.ForeignKey(Redditor, related_name='trades1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(Redditor, related_name='trades2', on_delete=models.CASCADE)
    comment_id = models.CharField(max_length=7)
    comment_url = models.CharField(max_length=200)

    def get_comment_url(self):
        comment = reddit.comment(self.comment_id)
        return 'https://www.reddit.com' + comment.permalink