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
EMPTY_JSON_PATH = cp.get("customs", "emptyjson")
with open(EMPTY_JSON_PATH, "r") as fp:
	EMPTY_JSON = json.load(fp)
RELOAD = cp.get("self", "reload")
DEBUG = cp.get("self", "debug")

app = bottle.Bottle()
CACHE = LRUCache(maxsize=CACHE_MAXSIZE)


def json_load(blah):
	with open(os.path.join(BLAH_PATH, blah)) as data_file:
		return json.load(data_file)


def json_update(blah_dict, key_list, value):
	reduce(dict.__getitem__, key_list[:-1], blah_dict).update({key_list[-1]:value})
	return blah_dict


def json_write(blah_name, data):
	f = os.path.join(BLAH_PATH, blah_name)
	with open(f,"w") as data_file:
		json.dump(data, data_file)


def key_recurse(blah_dict, key_list):
	try:
		if len(key_list) == 1:
			return blah_dict[key_list.pop()]
		return key_recurse(blah_dict[key_list.pop()], key_list)
	except KeyError as e:
		print "Key not found : %s" % e
		return EMPTY_JSON
	except TypeError as e:
		print "TypeError : %s " % e
		return EMPTY_JSON

def find_broken_link(l, d):
	accepted = []
	output = None
	for key in l:
		try:
			if isinstance(d, dict):
				d = d[key]
				accepted.append(key)
			else:
				print "reached non dict dead end"
				output = key
				break
		except KeyError as k:
			output = key
			break
	return output, accepted


def deep_append(path, target, value):
	steps = []
	for key in path[:-1]:
		steps.append([key, target[key]])
		target = target[key]
	steps.append([path[-1], value])
	
	while len(steps) > 1:
		k = steps.pop()
		try:
			print "[DeepAppend]: appending new branch"
			steps[-1][1].update({k[0]:k[1]})
		except AttributeError as ae:
			print "[DeepAppend]: promoting leaf to branch"
			steps[-1][1] = {k[0]:k[1]}

	return steps

def prepare_graph(path,target):
	broken, walked = find_broken_link(path, target)
	
	if broken is None:
		print "tree is OK"
		return False

	print "Found broken path at %s" % broken

	to_append = path[len(walked):]

	for branch in to_append:
		walked.append(branch)
		target = deep_append(walked, target, {})[0]
		target = {target[0]:target[1]}

	return target

@app.route("/blah/<blah>")
def get_whole_blah(blah):
	try:
		output = CACHE[blah]
	except KeyError as e:
		try:
			print "Blah %s not cached, caching" % blah
			CACHE[blah] = json_load(blah)
		except IOError as f:
			print "Blah %s not stored in bbbase" % blah
			#CACHE[blah] = EMPTY_JSON
			#output = CACHE[blah]
			output = EMPTY_JSON
			return output
		output = get_whole_blah(blah)
	return output


@app.route("/get/<blah>/<key:path>")
def get_blah(blah, key):
	blah_dict = get_whole_blah(blah)
	key_list = key.split("/")[::-1]
	return key_recurse(blah_dict, key_list)

	
@app.route("/set/<blah>/<key:path>/<value>")
def set_value_in_blah(blah, key, value):
	print "set key %s to %s in %s" % (key, value, blah)
	blah_dict = get_whole_blah(blah)
	key_list = key.split("/")
	#blah_dict = json_update(blah_dict, key_list, value)
	update_branch = prepare_graph(key_list, blah_dict)
	if update_branch:
		blah_dict[key_list[0]] = update_branch[key_list[0]]

	da = deep_append(key_list, blah_dict, value)[0]
	blah_dict.update({da[0]:da[1]})
	json_write(blah, blah_dict)
	CACHE[blah] = blah_dict
	return blah_dict

		
app.run(host=HOST, port=PORT, debug=DEBUG, reloader=RELOAD)

