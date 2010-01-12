from cloudsn.providers.facebook import Facebook

if __name__ == '__main__':
    api_key = 'd010cb3718b7fae4aa0efbb6e03403a9'
    secret_key = '166ae7fc00234f750943da222cf72558'

    if True:
        uid = '1147266555'
        sk = '2.cTKqW5UBLPt_muXln7mWUw__.86400.1263409200-1147266555'
        user_secret = 'P2Q2Lpj4gJiSpo49H4vhSQ__'
        facebook = Facebook(api_key, secret_key)
        facebook.desktop = True
        facebook.uid = '1147266555'
        facebook.session_key = sk
        #facebook.secret = user_secret
        facebook.auth.createToken()
        #result = facebook.auth.getSession()
        #facebook.secret = '2fe02f3f91bbb6f1afdf8c23205aa514'
    else:
        # Show login window
        # Set popup=True if you want login without navigational elements
        facebook = Facebook(api_key, secret_key)
        facebook.auth.createToken()
        facebook.login()
        print 'After logging in, press enter...'
        raw_input()
        result = facebook.auth.getSession()
    #facebook.session_key = session_key
    # Login to the window, then press enter
    

    
    print 'Session Key:   ', facebook.session_key
    print 'Your UID:      ', facebook.uid
    print 'Auth: ', facebook.auth_token
    print 'Secret: ', facebook.secret
    
    temp = facebook.status.get()
    print temp

    info = facebook.users.getInfo([facebook.uid], ['name', 'birthday', 'affiliations', 'sex'])[0]

    print 'Your Name:     ', info['name']
    print 'Your Birthday: ', info['birthday']
    print 'Your Gender:   ', info['sex']

    friends = facebook.friends.get()
    friends = facebook.users.getInfo(friends[0:5], ['name', 'birthday', 'relationship_status'])

    for friend in friends:
        print friend['name'], 'has a birthday on', friend['birthday'], 'and is', friend['relationship_status']

    arefriends = facebook.friends.areFriends([friends[0]['uid']], [friends[1]['uid']])

    photos = facebook.photos.getAlbums(facebook.uid)


