import webapp2
import jinja2
from google.appengine.api import users
import os
import json
from google.appengine.ext import ndb
from evdatabase import EvDatabase
from evdatabase import Review
from datetime import datetime

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
			template_values = {
				'url':url,
				'url_string':url_string
			}
			template = JINJA_ENVIROMENT.get_template('main.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect('/dashboard')



JINJA_ENVIROMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True
)

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/dashboard', Dashboard),
	('/add', AddVehicle),
	('/show/(.*)', ShowVehicle),
	('/edit/(.*)', EditVehicle),
	('/delete/(.*)', DeleteVehicle),
	('/compare/(.*)', CompareVehicle),
	('/get_ev/$', CheckDuplicateEv),
], debug=True)
