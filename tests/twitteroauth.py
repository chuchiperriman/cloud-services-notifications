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
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_url = auth.get_authorization_url()
    print 'Please authorize in your browser'
    
    webbrowser.open(auth_url)
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)
    ACCESS_KEY = auth.access_token.key
    ACCESS_SECRET = auth.access_token.secret
    
    #Access to twitter with the access keys
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    #api.update_status("Testing cloudsn with tweety")
    public_tweets = api.public_timeline()
    for tweet in public_tweets:
        print tweet.text
        
if __name__ == '__main__':
    main()
