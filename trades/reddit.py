import praw

def parse_praw_file():
    with open('trades/praw.txt', 'r') as file:
        lines = file.read().split('\n')
        return praw.Reddit(client_id=lines[0], client_secret=lines[1], user_agent=lines[2])

reddit = parse_praw_file()