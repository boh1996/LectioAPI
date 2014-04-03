import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append("..")
from config import *
found = False
try:
	import requesocks as requests
	found = True
except Exception, e:
	found = False
session = requests.session()
if found and USE_REQUEST_PROXY:
	session.proxies = {'http': 'socks5://127.0.0.1:9050',
                   'https': 'socks5://127.0.0.1:9050'}