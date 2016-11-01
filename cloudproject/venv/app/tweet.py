from tweepy.streaming import StreamListener
#from HTMLParser import HTMLParser
from tweepy import OAuthHandler
from tweepy import Stream
from http.client import IncompleteRead
import logging
from array import *
#import timecmd
import collections
from flask import jsonify
import threading
import json
from elasticsearch import Elasticsearch
from flask import Flask, render_template, request

app = Flask(__name__)

lock = threading.Lock()
es = Elasticsearch()

_log = logging.getLogger(__name__)

# User credentials to access Twitter API
access_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
consumer_key='xxxxxxxxxxxxxxxx'
consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
i = [0]
coord = []

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		#try:
		result = request.form['option']
		if result is not None:
			print (result)
			searchtext = "text" + ":" +result
			print (searchtext)
			res = es.search(index='test', q='searchtext')
			for hit in res['hits']['hits']:
				coord.append (hit["_source"]["coordinates"]["coordinates"])
				print("%(coordinates)s: %(text)s" % hit["_source"])
			print("**********************************************************")
			print (coord)
			return render_template("index.html", result = coord)
		else:
			print ("error reading ")
			return "ERROR"
		#except httplib.IncompleteRead as e:
			#result = "null"
	else:
		tv_show = "The Office"
		return render_template("index.html")
	

class TwitterListener(StreamListener):

	
	def __init__(self, phrases):
		auth = OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		try:
			self.__stream = Stream(auth, listener=self)
			self.__stream.filter(track=phrases, async=True)
		except IncompleteRead:
			pass

		
	def disconnect(self):
		self.__stream.disconnect()

	def on_data(self, data):
		dic = collections.OrderedDict()
		i[0] += 1
		try:
			data = json.loads(data)
			if data['coordinates'] and data['text']:
				with lock:
					with open("output.json", "a") as f:
						f.write("here")
						f.write(str(data))
						print(data)
						dic['id'] = data['id']
						dic['text'] = data['text']
						dic['coordinates'] = data['coordinates']
						jsonArray = json.dumps(dic)
						es.index(index="test", doc_type='tweet', id=data['id'], body=jsonArray) 
						print(data['coordinates'], data['text'])
						print("data written")
						
			return True
		except BaseException as e:
			print(str(e))
			return True
		except attributeerror as e:
			print(str(e))
			return True
		except keyerror as e:
			print(str(e))
			return True
		except exception as e:
			print(str(e))
			return True


	def on_error(self, status):
		print(status)
		return True

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)

	phrases = ['trump', 'debate', 'obama', 'clinton', 'technology', 'NBA', 'movie', 'crime', 'ADHM', 'cricket']
	listener = TwitterListener(phrases)
	app.run()
