import sys
import csv

FILE = "/tmp/sample.csv"

def main():
    
    feeds = dict()
    feeds['a'] = ('1','aaa')
    feeds['b'] = ('2','bbb')
    feeds['c'] = ('5','ccc')
    feeds['d'] = ('4','ddd')
    feeds['e'] = ('3','eee')
    
    """
    data = [
        ("And Now For Something Completely Different", 1971, "Ian MacNaughton"),
        ("Monty Python And The Holy Grail", 1975, "Terry Gilliam, Terry Jones"),
        ("Monty Python's Life Of Brian", 1979, "Terry Jones"),
        ("Monty Python Live At The Hollywood Bowl", 1982, "Terry Hughes"),
        ("Monty Python's The Meaning Of Life", 1983, "Terry Jones")
    ]
    """
    rows = sorted(feeds.values(), key=lambda x: x[0])
    print rows
    print rows[2:]
    return
    writer = csv.writer(open(FILE, "a+"), delimiter='\t')

    """
    for item in data:
        writer.writerow(item)
        
    writer.writerows(data)
    """
    writer.writerows(feeds.values())
        
    
    reader = csv.reader(open(FILE), delimiter='\t')

    for feed_id, feed_title in reader:
        print feed_id, feed_title

    name="Chuchi Perriman ()-@!$%&"
    print "-" + "".join([x for x in name if x.isalpha() or x.isdigit()]) + "-"
    
if __name__ == '__main__':
    sys.exit(main())

    
