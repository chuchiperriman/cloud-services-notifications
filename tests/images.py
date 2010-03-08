import Image

path = '/home/perriman/dev/cloud-services-notifications/data'

error = Image.open(path + '/error.png')
gmail = Image.open(path + '/twitter.png')
gmail.paste (error, (10,10), error)
gmail.save ('/tmp/aaa.png')

