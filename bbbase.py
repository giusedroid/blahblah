__author__ = 'Giuseppe Battista'
__description__ = 'This is the dumbest database ever. If you\'re using it for smart purposes, the joke\'s on you.'

import bottle
import ConfigParser
import json
from cachetools import LRUCache
import os

cp = ConfigParser.ConfigParser()

conf = cp.read("conf/conf")

HOST = cp.get("self", "host")
PORT = cp.get("self", "port")
CACHE_MAXSIZE = cp.get("cache", "maxsize")
BLAH_PATH = cp.get("self", "blahpath")
EMPTY_JSON = cp.get("customs", "emptyjson")
DEBUG = cp.get("self", "debug")

app = bottle.Bottle()

CACHE = LRUCache(maxsize=CACHE_MAXSIZE)

def load_json(blah):
	with open(os.path.join(BLAH_PATH, blah)) as data_file:
		return json.load(data_file)


@app.route("/load/<blah>")
def load_blah(blah):
	CACHE[blah] = load_json(blah)
	return '{"blah":"blah %s loaded"}' % blah

@app.route("/blah/<blah>")
def get_whole_blah(blah):
	try:
		output = CACHE[blah]
	except KeyError as e:
		try:
			print "Blah %s not cached, caching" % blah
			CACHE[blah] = load_json(blah)
		except IOError as f:
			print "Blah %s not stored in bbbase" % blah
			CACHE[blah] = EMPTY_JSON
			output = CACHE[blah]
		output = get_whole_blah(blah)
	return output


app.run(host=HOST, port=PORT, debug=True)
