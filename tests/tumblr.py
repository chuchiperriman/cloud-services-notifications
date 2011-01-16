import urllib2
import urllib
import xml.dom.minidom

params = {'email': 'chuchiperriman@gmail.com', 'password': ''}
params = urllib.urlencode(params)
f = urllib2.urlopen('http://www.tumblr.com/api/dashboard', params, 20)
data = f.read()
print data

feeds=list()

def processPost (post):
    post_type = post.getAttribute("type")
    
    if post_type == 'link':
        print "Post link:", post.getElementsByTagName("link-text")[0].childNodes[0].nodeValue
        print "Post link url:", post.getElementsByTagName("link-url")[0].childNodes[0].nodeValue
    
    """
	for c in ob.getElementsByTagName ("post"):
		if c.getAttribute("name") == "id":
			ftype, s, feed = c.childNodes[0].nodeValue.partition("/")
			self.feeds.append({"type" : ftype,
					   "feed" : feed})
			break

	for c in ob.getElementsByTagName ("number"):
		if c.getAttribute("name") == "count":
			self.feeds[-1]["count"] = c.childNodes[0].nodeValue
			break
    """
doc = xml.dom.minidom.parseString(data)
elist = doc.childNodes[0].getElementsByTagName("posts")[0]
print 'ues'
for post in elist.getElementsByTagName("post"):
	processPost (post)


