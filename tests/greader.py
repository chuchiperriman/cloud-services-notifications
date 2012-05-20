import os, sys, re

srcpath = os.path.abspath("../src")
sys.path.insert(0,srcpath)

import traceback, urllib2, httplib, urllib, simplejson
import cookielib
import webbrowser
from cloudsn.providers.greaderprovider import *


SCOPE = 'https://www.google.com/reader/api'
def main():
    #Ask for permissions and set the pin
    #password = raw_input('password: ').strip()
    cookiejar = cookielib.CookieJar()
    _cproc = urllib2.HTTPCookieProcessor(cookiejar)
    opener = urllib2.build_opener(_cproc)
    urllib2.install_opener(opener)
    url = 'https://accounts.google.com/o/oauth2/auth?client_id=%s&redirect_uri=%s&response_type=%s&scope=%s' \
            % (CLIENT_ID, REDIRECT_URI, \
               'code', SCOPE)
          
    webbrowser.open (url)
    pin = raw_input('PIN: ').strip()
    
    params = {'client_id' : CLIENT_ID,
	              'client_secret': CLIENT_SECRET,
	              'code': pin,
	              'redirect_uri': REDIRECT_URI,
	              'grant_type' : 'authorization_code',
	              'scope' : SCOPE,
	              }
    f = opener.open ('https://accounts.google.com/o/oauth2/token', urllib.urlencode(params))
    data = f.read()
    print data
    data = simplejson.loads(data)
    
    params = {'client_id' : CLIENT_ID,
	              'client_secret': CLIENT_SECRET,
	              'grant_type' : 'refresh_token',
	              'refresh_token' : data['refresh_token'],
	              }
    f = opener.open ('https://accounts.google.com/o/oauth2/token', urllib.urlencode(params))
    data = f.read()
    print data
    data = simplejson.loads(data)
    
    """
    request = urllib2.Request(r"https://www.google.com/reader/api/0/unread-count")
    request.add_header("Authorization", "Bearer " + data["access_token"])

    data = urllib2.urlopen(request).read()
    print data
    return
    """
    
    url = SCOPE + '?access_token='+ data['access_token']
    print url
    f = opener.open(url)
    data = f.read()
    print data
    return
    match_obj = re.search(r'SID=(.*)', data, re.IGNORECASE)
    sid = match_obj.group(1) if match_obj.group(1) is not None else ''
    print sid
    match_obj = re.search(r'LSID=(.*)', data, re.IGNORECASE)
    lsid = match_obj.group(1) if match_obj.group(1) is not None else ''
    print lsid
    
    cookiejar.add_cookie(req, 'cname2', 'cval2',
                {'expires':  int(time.time()) + 3600,})
    
    f = opener.open('http://www.google.com/reader/api/0/token')
    print f.read()
    
        
if __name__ == '__main__':
    main()
