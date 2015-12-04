__author__ = 'Giuseppe Battista'
__description__ = 'This is the dumbest database ever. If you\'re using it for smart purposes, the joke\'s on you.'

import bottle
import ConfigParser
import json
from cachetools import LRUCache
import os

cp = ConfigParser.ConfigParser()

cp.read("conf/conf")

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


def make_blah(blah):
	f = os.path.join(BLAH_PATH, blah)
	if not os.path.isfile(f):
		with open(f,"w") as data_file:
			data_file.writeln(EMPTY_JSON)
			data_file.flush()

def recurse_key(blah_dict, key_list):
		if len(key_list) == 1:
			return blah_dict[key_list.pop()]
		return recurse_key(blah_dict[key_list.pop()], key_list)

def load_blah(blah):
	try:
		CACHE[blah] = load_json(blah)
		output = '{"blah":"blah %s loaded"}' % blah
	except IOError as e:
		print "%s not found, returning standard empty json" % blah
		output = EMPTY_JSON
	return output


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


@app.route("/blah/<blah>/<key:path>")
def get_blah(blah, key):
	blah_dict = get_whole_blah(blah)
	key_list = key.split("/")[::-1]
	return recurse_key(blah_dict, key_list)
	
		

app.run(host=HOST, port=PORT, debug=True)
