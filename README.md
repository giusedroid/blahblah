# blahblah

This is the dumbest slowest database ever. If you are going to use it for smart fast purposes, it will disappoint you. 

The reason I waste my time writing it is I need to store some values across many different scripts and computers and cannot and won't bother setting up a real database with authentication and blah blah. Also, I use it to make mock REST API JSON responses.

Feel free to blah blah your data here.

##Prerequisites
python 2.7

pip install bottle cachetools 

##Optionals
pip install cherrypy

##Launch 
python bbbase.py &

##Usage / Test:
curl http://localhost:8088/set/your_file/key/value

curl http://localhost:8088/get/your_file/key

Supports nested objects.

##Configurations

[self]

host = localhost

port = 8088

blahpath = blahs

debug = False

reload = False

[cache]

maxsize = 5

[customs]

\# path to default empty object

emptyjson = blahs/empty

##Contacts
http://giusedroid.blogspot.com

@giusedroid on Twitter
