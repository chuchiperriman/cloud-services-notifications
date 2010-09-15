import traceback, urllib2, httplib
from cloudsn.providers import oauth

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

class Api:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __handle_oauth(self):
        self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        self.sign_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.access_url = 'https://api.twitter.com/oauth/access_token'

        try:
            request = oauth.OAuthRequest.from_consumer_and_token(
                oauth_consumer=self.consumer,
                http_method='POST', http_url=self.access_url,
                parameters = {
                    'x_auth_mode': 'client_auth',
                    'x_auth_username': self.username,
                    'x_auth_password': self.password
                }
            )
            print '1'
            request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)
            print '2',request.to_postdata()
            req = urllib2.Request(self.access_url, data=request.to_postdata())
            response = urllib2.urlopen(req)
            print '3'
            self.token = oauth.OAuthToken.from_string(response.read())

        except Exception, error:
            print "Error: %s\n%s" % (error, traceback.print_exc())
    def auth(self):
        self.__handle_oauth()
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                        token=self.token, http_method=method, http_url=uri,
                        parameters=params)
if __name__ == '__main__':
    a = Api('chuchiperriman', 'la3t1t1a')
    a.auth()


### DJANGO VIEWS BELOW THIS LINE

"""
def main(request):
    if request.get_host().startswith('www.') or '/labs/followers/' in request.path: # Should really be middleware
        return HttpResponseRedirect("http://fourmargins.com/labs/following/")
    if request.session.has_key('access_token'):
        return HttpResponseRedirect('/list/')
    else:
        return render_to_response('oauth/base.html')

def unauth(request):
    response = HttpResponseRedirect('/')
    request.session.clear()
    return response

def auth(request):
    "/auth/"
    token = get_unauthorised_request_token()
    auth_url = get_authorisation_url(token)
    response = HttpResponseRedirect(auth_url)
    request.session['unauthed_token'] = token.to_string()
    return response

def return_(request):
    "/return/"
    unauthed_token = request.session.get('unauthed_token', None)
    if not unauthed_token:
        return HttpResponse("No un-authed token cookie")
    token = oauth.OAuthToken.from_string(unauthed_token)
    if token.key != request.GET.get('oauth_token', 'no-token'):
        return HttpResponse("Something went wrong! Tokens do not match")
    access_token = exchange_request_token_for_access_token(token)
    response = HttpResponseRedirect('/list/')
    request.session['access_token'] = access_token.to_string()
    return response

def get_friends(request):
    users = []

    access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse("You need an access token!")
    token = oauth.OAuthToken.from_string(access_token)

    # Check if the token works on Twitter
    auth = is_authenticated(token)
    if auth:
        # Load the credidentials from Twitter into JSON
        creds = simplejson.loads(auth)
        name = creds.get('name', creds['screen_name']) # Get the name

        # Get number of friends. The API only returns 100 results per page,
        # so we might need to divide the queries up.
        friends_count = str(creds.get('friends_count', '100'))
        pages = int( (int(friends_count)/100) ) + 1
        pages = min(pages, 10) # We only want to make ten queries



        for page in range(pages):
            friends = get_friends(token, page+1)

            # if the result is '[]', we've reached the end of the users friends
            if friends == '[]': break

            # Load into JSON
            json = simplejson.loads(friends)

            users.append(json)

    return render_to_response('oauth/list.html', {'users': users})
"""

