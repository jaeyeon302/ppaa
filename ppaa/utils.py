import urllib.request as req
from urllib import parse
import traceback as tb

class objFromDict(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [objFromDict(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, objFromDict(b) if isinstance(b, dict) else b)
			

def complete_link(link,query_string=None):
	if link.startswith('http://') or link.startswith('https://'):
		return link
	if link.startswith('http:/'):
		link = 'http://'+link[len('http:/'):]
	elif link.startswith('https:/'):
		link = 'https://'+link[len('https:/'):]
	else:
		link = 'http://'+link
		
	if query_string:
		query_string = query_string.decode('utf-8')
		link += "?{}".format(query_string)
	return link	
	
def validate_link(link):
	res = None
	try:
		url = req.urlopen(link)
		if url.getcode() < 400: res=True
		else: res=False
	except:
		tb.print_exc()
		res = False
	print("validate : {} / link :{}".format(res,link))
	return res
	