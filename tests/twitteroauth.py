import traceback, urllib2, httplib
from cloudsn.providers import tweepy

SERVER = 'twitter.com'
PORT = 80

CONSUMER_KEY = 'uRPdgq7wqkiKmWzs9rneJA'
CONSUMER_SECRET = 'ZwwhbUl2mwdreaiGFd8IqUhfsZignBJIYknVA867Ieg'
REQUEST_TOKEN_URL = 'http://twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'http://twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'http://twitter.com/oauth/authorize'

# We use this URL to check if Twitters oAuth worked
TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'
TWITTER_FRIENDS = 'https://twitter.com/statuses/friends.json'

#connection = httplib.HTTPSConnection(SERVER)
#consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
#signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

def main():
    print 'aaaa'
    """
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_url = auth.get_authorization_url()
    print 'Please authorize: ' + auth_url
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)
    print "ACCESS_KEY = '%s'" % auth.access_token.key
    print "ACCESS_SECRET = '%s'" % auth.access_token.secret
    """
    ACCESS_KEY = '99826588-h2IQbsHR3Udj7tQUzNslD01cRnGnI4nm5wieQNqdY'
    ACCESS_SECRET = 'tBwyH4cE3qztGCEQchurF8tpZHYMlBWRlltqAG9Qrs'

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    #api.update_status("Testing cloudsn with tweety")
    print api.public_timeline()[0].user.name
if __name__ == '__main__':
    main()
