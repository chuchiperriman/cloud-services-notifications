import os, sys

srcpath = os.path.abspath("../src")
sys.path.insert(0,srcpath)

import traceback, urllib2, httplib
import webbrowser
from cloudsn.providers import tweepy

CONSUMER_KEY = 'uRPdgq7wqkiKmWzs9rneJA'
CONSUMER_SECRET = 'ZwwhbUl2mwdreaiGFd8IqUhfsZignBJIYknVA867Ieg'

def main():
    #Ask for permissions and set the pin
    password = raw_input('password: ').strip()
    auth = tweepy.BasicAuthHandler("chuchiperriman", password)
    api = tweepy.API(auth, "identi.ca",api_root="/api")
    #api.update_status("Testing cloudsn with tweety")
    public_tweets = api.public_timeline()
    for tweet in public_tweets:
        print tweet.text
        
if __name__ == '__main__':
    main()
