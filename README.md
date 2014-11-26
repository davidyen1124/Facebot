Facebot
=======

Send facebook message to person or group
----------------------------------------
Graph API doesn't provide function for sending message, so I write one.

You can write a bot to talk with you, or send notification to your co-workers group if one of your server is down.

Installation
------------
`pip install facebot`

or

`python setup.py install`

Usage
-----
###Initiate a facebook instance:
```
	>>> from facebot import Facebook
	>>> f = Facebook('<USERNAME>', '<PASSWORD>')
```

###Send message to a person:
```
	# send a text message
	>>> f.send_person('<USER_ID>', '<BODY>') 
	
	# send message with photo
	>>> f.send_person('<USER_ID>', '<BODY>', 'http://imgs.xkcd.com/comics/python.png')
```

###Send message to the group:
How to find thread id?

Select `See Full Conversaction` in the group dialog, and the last part of url should be `conversaction-123456789`, so `123456789` is the thread id.
```
	# send a text message
	>>> f.send_group('<THREAD_ID>', '<BODY>') 
	
	# send message with photo
	>>> f.send_person('<THREAD_ID>', '<BODY>', 'http://imgs.xkcd.com/comics/python.png')
```

###Get access token:
```
	# default using Graph API Explorer
	>>> f.get_access_token()
	
	# retrieve other app's access token
	>>> f.get_access_token('<APP_ID>')
```
