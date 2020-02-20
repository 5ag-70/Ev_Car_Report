import webapp2
import jinja2
from google.appengine.api import users
import os
from google.appengine.ext import ndb
from evdatabase import EvDatabase
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

class Dashboard(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		evs = EvDatabase.query().order(-EvDatabase.date).fetch()
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			url_string = 'logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
		template_values = {
			'url':url,
			'url_string':url_string,
			'user':user,
			'evs':evs,
		}
		template = JINJA_ENVIROMENT.get_template('dashboard.html')
		self.response.write(template.render(template_values))

	def post(self):
		request = self.request.POST
		search_string = ''
		if not (request['start']) == '':
			start = request['start']
		if not (request['end']) == '':
			end = request['end']
		search = request['search'].strip().capitalize()
		ev_data = request['ev_data']
		if ev_data == 'name':
			evs = EvDatabase.query().filter(EvDatabase.name == search).fetch()
			search_string = 'cars having name ' + search
		elif ev_data == 'manufacturer':
			evs = EvDatabase.query().filter(EvDatabase.manufacturer == search).fetch()
			search_string = 'cars manufactured by ' + search
		elif ev_data == 'year':
			evs = EvDatabase.query(EvDatabase.year >= int(start), EvDatabase.year <= int(end)).fetch()
			search_string = 'cars manufactured in year ' + start + ' to ' + end
		elif ev_data == 'battery_size':
			evs = EvDatabase.query(EvDatabase.battery_size >= int(start), EvDatabase.battery_size <= int(end)).fetch()
			search_string = 'cars having battery size from ' + start + ' to ' + end
		elif ev_data == 'range':
			evs = EvDatabase.query(EvDatabase.range >= int(start), EvDatabase.range <= int(end)).fetch()
			search_string = 'cars having range of ' + start + ' to ' + end + ' Km'
		elif ev_data == 'cost':
			evs = EvDatabase.query(EvDatabase.cost >= int(start), EvDatabase.cost <= int(end)).fetch()
			search_string = 'cars selling at price point of ' + start + ' to ' + end
		elif ev_data == 'power':
			evs = EvDatabase.query(EvDatabase.power >= int(start), EvDatabase.power <= int(end)).fetch()
			search_string = 'cars having power ranging from ' + start + ' to ' + end
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			url_string = 'logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
		template_values = {
			'url':url,
			'url_string':url_string,
			'user':user,
			'evs':evs,
			'search_string':search_string
		}
		template = JINJA_ENVIROMENT.get_template('dashboard.html')
		self.response.write(template.render(template_values))

class AddVehicle(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			url_string = 'logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
		template_values = {
			'url':url,
			'url_string':url_string,
			'user':user
		}
		template = JINJA_ENVIROMENT.get_template('add-vehicle.html')
		self.response.write(template.render(template_values))

	def post(self):
		request = self.request.POST
		name = request['vname'].strip().capitalize()
		manufacturer = request['manufacturer'].strip().capitalize()
		year = request['year']
		battery_size = int(request['bsize'])
		range = int(request['range'])
		cost = int(request['cost'])
		power = int(request['power'])
		user = users.get_current_user()
		created_by = user
		carkey = manufacturer+name+year
		date = datetime.now()
		evexist = EvDatabase.query(EvDatabase.carkey==carkey).get()
		if(evexist == None):
			evdatabase = EvDatabase(name=name,
								manufacturer=manufacturer,
								year=int(year),
								battery_size=battery_size,
								range=range,
								cost=cost,
								power=power,
								created_by=user,
								carkey=carkey,
								date=date,)
			evdatabase.put()
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

], debug=True)
