import urllib.request as req
from urllib import parse
import traceback as tb
from ppaa.config import mail_config
from flask import request as req
import requests
import functools


class objFromDict(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [objFromDict(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, objFromDict(b) if isinstance(b, dict) else b)
			
mail_conf = objFromDict(mail_config())
def send_mail(to,subject,txt=None,html=None,from_addr="PPAA Support <support@ppaa.me>"):
	if not isinstance(to,list):to = [to]
	
	return requests.post(
		mail_conf.ADDRESS,
		auth=('api',mail_conf.API_KEY),
		data={'from':from_addr,
			 'to':to,
			 'subject':subject,
			 'text':txt,
			 'html':html})

			
			
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
		print(link)
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

def add_funcname_to_print(f):
	name = "{}.{}".format(f.__module__,f.__name__)
	def new_print(val,**kwargs):
		print("func: {} | {}".format(name,val),**kwargs)
	@functools.wraps(f)
	def wrapped(*args,**kwargs):
		return f(new_print,*args,**kwargs)
	return wrapped

def add_timestamp_to_stdout():
	from sys import stdout
	from datetime import datetime
	from pytz import timezone
	KST = timezone('Asia/Seoul')
	origin_out = stdout.write
	def out(txt):
		time = datetime.now(KST).isoformat()
		if txt !='\n':
			txt = "{} | {}".format(time,txt)
		origin_out(txt)
	stdout.write = out
	
def add_ipaddr_to_stdout():
	from sys import stdout
	from flask import request, has_request_context
	origin_out = stdout.write
	def out(txt):
		ipaddr=""
		if has_request_context():ipaddr="{} | ".format(req.remote_addr)
		if txt != "\n": txt="{}{}".format(ipaddr,txt)
		origin_out(txt)
	stdout.write = out
	
def set_print_format():
	add_timestamp_to_stdout()
	add_ipaddr_to_stdout()
	
