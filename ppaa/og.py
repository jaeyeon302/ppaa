import opengraph_py3 as og
import msgpack as mg
import ssl
import traceback as tb

from urllib.request import Request, urlopen
from ppaa.utils import objFromDict, add_funcname_to_print, validate_link
from ppaa.db import get_db
from os.path import join

DEFAULT_IMG = "https://lh3.googleusercontent.com/evp44qqJ5gKPuTUOCY2Ma7GYfgQQLa2ad39qJPmyU2lf1qaZj27V_N1IKhf0BUZY_72w1wRHKOFIY2TKrW2SVjm1S75CcK6Rn1i1zjAkMaFlGzyH6s1icLB2mK6BZXFHM_OTAyfvQk2MMswXhhq2eU-6Rh9a6LLQIES5NcScLAwPz811L34NVMw10bg7TA1D3wk5ledQM3fifKitlK_RLoB-IRsYP78z6ZG1_IUlzA5DNH3eDbtNiMWcKQTtmEOwRa8oYYxAFaoSF5v6b-FKHNNhLpCzLVgfmS3Lg_IsCLslVfqryB-uT7VFLzM1cd7-2VwEwQCvXU75ApKEBwn3f_FG36f-JsvHhQO89F-dgpWYBmITy-KvpVTOTDCBZ9C27yJQHCs2Ka9ps8hTGa8vhMndc9mvH7YWbSgSmjjdJ8dPeyan5flCxv-xypk45wbLeuOEi0t7GMVgowHmb0UKMWebu-9mF8Drg0z_a3J7bbvkGYD9W9wyd9ed1cC2WMfQTISC7xLzkkfkR2PmWNm_f8cDr7jdQi0SZfQRRUFH5BCBGeKIvcLMpVi2UX5_YvhgGowSRYmzYVrsJizpqOjgTFbZNjMhAzrGCS6HvVDC6McEdqoVLZ4ZtSUckbQm3yYlcNk8fwus2w8prtrgosiPvjNQqy66S2GJxqfhl42-ZkMvul8q12aDRTlO3_C1nyDtwg7NCS-1vX1HHT5fB1EqQxTMEw=w418-h252-no"



@add_funcname_to_print
def add_ogtag(print,link,default_img=None):
	db = get_db()
	req = Request(link,headers={'User-Agent':'Mozilla/5.0'})
	print(req.__dict__)
	context = ssl._create_unverified_context()
	try:
		html = urlopen(req,context=context,timeout=2)
		meta_og = og.OpenGraph(html=html.read(),scrape=True)
	except:
		print(tb.format_exc())
		meta_og = og.OpenGraph()
	if not meta_og.valid_attr('title'):meta_og.title = req.host
	if not meta_og.valid_attr('image'):meta_og.image = default_img
	if not meta_og.valid_attr('description'):meta_og.description = link
	
	print(meta_og)
	if meta_og.image is not None and not meta_og.image.startswith('http') and meta_og.image != "":
		if meta_og.image.startswith('/'):
			root = req.host
		else:
			root = req.host + req.selector[:req.selector.rfind('/')]
		imgsrc = "{}://{}/{}".format('http',root,meta_og.image)
		meta_og.image = imgsrc
		
	bin_og = mg.packb(meta_og,use_bin_type=True)
	already_inserted = db.execute('SELECT id FROM meta WHERE link=?',(link,)).fetchone()
	if already_inserted:
		db.execute('UPDATE meta SET bin_meta=? WHERE link=?',(bin_og,link))
	else:
		db.execute('INSERT INTO meta (link,bin_meta)VALUES(?,?)',(link,bin_og))
	db.commit()
	print("refresh og tag / link:{}".format(link))
	return True
	
@add_funcname_to_print
def get_ogtag(print,link):
	db = get_db()
	bin_og = db.execute('SELECT bin_meta FROM meta WHERE link=?',(link,)).fetchone()
	if not bin_og:
		return None
	else:
		bin_og = bin_og['bin_meta']
		meta_og = mg.unpackb(bin_og,raw=False)
		meta_og = objFromDict(meta_og)
		return meta_og
	
def render_ogtag(ogtag):
	title = ogtag.title
	description = ogtag.description
	img_src = ogtag.image
	