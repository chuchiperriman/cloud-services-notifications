import Image
import gtk

path = '/home/perriman/dev/cloud-services-notifications/data'

error = Image.open(path + '/error.png')
gmail = Image.open(path + '/twitter.png')
gmail.paste (error, (10,10), error)
gmail.save ('/tmp/aaa.png')


pixbuf = gtk.gdk.pixbuf_new_from_file(path + '/twitter.png')
pixbuf2 = gtk.gdk.pixbuf_new_from_file(path + '/error.png')
pixbuf2.composite(pixbuf, 10, 10, 22, 22, 10, 10, 1.0, 1.0, gtk.gdk.INTERP_HYPER, 220)

## now pixbuf2 contains the result of the compositing operation
pixbuf.save("/tmp/zbr.png", 'png')
