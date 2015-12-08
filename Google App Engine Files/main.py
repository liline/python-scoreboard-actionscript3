#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.ext import ndb
import logging
import cgi
import hashlib
import re

class HighScore (ndb.Model):
	username = ndb.StringProperty()
	userscore = ndb.IntegerProperty()

	@classmethod
	def query_scores(cls):
		return cls.query().order(-cls.userscore)

class MainHandler(webapp2.RequestHandler):

	def get (self):
		logging.info("MainHandler: GET")

	def post (self):
		logging.info("MainHandler: POST")

		# Please put in your own salt values and ensure they are the same on the client side
		salt = "first salt"
		salt2 = "second salt"
		randomString = "-ID"
		TOTAL_CHARS = 22

		self.response.headers['Content-Type'] = 'text/plain'

		try:
			score = int(self.request.get('score'))
		except ValueError:
			score = 0

		name = self.request.get('name')

		scoreHash = self.request.get('scoreHash')
		m = hashlib.md5();
		m.update(salt + str(score) + name )

		m2 = hashlib.md5();
		m2.update(salt2 + m.hexdigest());
		serverscoreHash = m2.hexdigest();

		# Give the hacker a bad score and email admin
		if scoreHash == serverscoreHash:
			logging.info("Valid: Same score hash")
			submit = True
		else:
			logging.info("Invalid: Hacks")
			score = -42
			submit = False

		if name == "":
			name = 'No Name'

		# no white spaces for name
		name = re.sub(r'\s+', ' ', name).strip()
		logging.info("***NAME:****" + name)

		# Unique ID to store in DB to prevent multiple entries
		uniqueid = name + str(score) +  randomString;
		logging.info("ID : " + uniqueid);

		# If scorehash is valid, let's prep the query and submit
		if submit:
			highscore = HighScore(username = name, userscore = score, id = uniqueid)
			highscore_key = highscore.put()
			highscore_key = highscore.put()
	  	topscores = HighScore.query_scores().fetch(10)
	  	logging.info ("fetched 10 " );

	  	for scoreentry in topscores:
	    		logging.info("Name: %s and Score: %s", str(scoreentry.username), str(scoreentry.userscore))

	  	if len(name) > 0:
	    		for scoreentry in topscores:
        			self.response.out.write('%s ' %cgi.escape(scoreentry.username))
        			currname = str(scoreentry.username)
        			logging.info("curr name : " + currname)
        			logging.info("curr name length : " + str(len(currname)))
        			logging.info("Length: %d ", len(name))
        			diff = TOTAL_CHARS - len(currname)
        			self.response.out.write(' ' * diff)
        			self.response.out.write('score: %s ' %str(scoreentry.userscore))
        			self.response.out.write('\n')

	  	else:
	    		self.response.out.write('Hello world!')


# Unused - example if you wanted another handler
class EmailHandler(webapp2.RequestHandler):
	def get (self):
		logging.info("Email Handler: GET")

	def post (self):
		logging.info("Email Handler: POST")

# Be sure to define your handlers and routes here
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/emailmoo/', EmailHandler)], debug=True)




