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

class CheckDuplicateEv(webapp2.RequestHandler):
	def post(self):
		response_data = {}
		request = self.request.POST
		name = request['name'].strip().capitalize()
		manufacturer = request['manufacturer'].strip().capitalize()
		year = request['year']
		car_key = manufacturer+name+year
		evexist = EvDatabase.query(EvDatabase.carkey==car_key).get()
		if evexist == None:
			response_data["ev_exist"] = False
		else:
			response_data["ev_exist"] = True
		self.response.headers['Content-Type'] = 'application/json'
		return self.response.out.write(json.dumps(response_data))

class ShowVehicle(webapp2.RequestHandler):
	def get(self, ev_id):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		url = ''
		url_string = ''
		if user:
			url = users.create_logout_url(self.request.uri)
			url_string = 'logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
		evs = EvDatabase.get_by_id(int(ev_id))
		reviews = Review.query(Review.carkey==evs.carkey).order(-Review.date).fetch()
		review_count = Review.query(Review.carkey==evs.carkey)
		count = review_count.count()
		average_score = 0.0
		if count is not 0:
			for review in reviews:
				average_score = average_score + review.rating
			average_score = round(average_score/count, 2)
			evs.average_score = average_score
			evs.put()
		average_score_int = int(average_score)
		template_values = {
			'url':url,
			'url_string':url_string,
			'user':user,
			'evs':evs,
			'reviews':reviews,
			'count':count,
			'average_score':average_score,
			'average_score_int':average_score_int,
		}
		template = JINJA_ENVIROMENT.get_template('show-vehicle.html')
		self.response.write(template.render(template_values))

	def post(self, ev_id):
		request = self.request.POST
		user = users.get_current_user()
		created_by = user
		review = request['review']
		rating = int(request['rating'])
		date = datetime.now()
		carkey = request['carkey']
		ev_id = request['ev_id']
		carreview = Review(created_by=created_by,
								review=review,
								rating=rating,
								date=date,
								carkey=carkey)
		carreview.put()
		self.redirect('/show/'+ev_id)

class EditVehicle(webapp2.RequestHandler):
	def get(self, ev_id):
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
		evs = EvDatabase.get_by_id(int(ev_id))
		template_values = {
			'url':url,
			'url_string':url_string,
			'user':user,
			'evs':evs
		}
		template = JINJA_ENVIROMENT.get_template('edit-vehicle.html')
		self.response.write(template.render(template_values))

	def post(self, ev_id):
		request = self.request.POST
		evdatabase = EvDatabase.get_by_id(int(ev_id))
		name = request['vname'].strip().capitalize()
		manufacturer = request['manufacturer'].strip().capitalize()
		year = int(request['year'])
		battery_size = int(request['bsize'])
		range = int(request['range'])
		cost = int(request['cost'])
		power = int(request['power'])
		evdatabase.name=name
		evdatabase.manufacturer=manufacturer
		evdatabase.year=year
		evdatabase.battery_size=battery_size
		evdatabase.range=range
		evdatabase.cost=cost
		evdatabase.power=power
		evdatabase.put()
		self.redirect('/show/'+ev_id)


class DeleteVehicle(webapp2.RequestHandler):
	def get(self, ev_id):
		evdatabase = EvDatabase.get_by_id(int(ev_id))
		evdatabase.key.delete()
		reviews = Review.query(Review.carkey == evdatabase.carkey).fetch()
		for review in reviews:
			if review is not None:
				review.key.delete()
		self.redirect('/dashboard')

class CompareVehicle(webapp2.RequestHandler):
	def get(self, data):
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
		try:
			import simplejson as json
		except(ImportError,):
			import json
		comparedata = json.loads(data)
		evs = []
		for data in comparedata:
			ev_data = EvDatabase.get_by_id(int(data))
			evs.append(ev_data)
		year_list = []
		battery_size_list = []
		range_list = []
		cost_list = []
		power_list = []
		average_score_list = []
		for ev in evs:
			year_list.append(ev.year)
			battery_size_list.append(ev.battery_size)
			range_list.append(ev.range)
			cost_list.append(ev.cost)
			power_list.append(ev.power)
			average_score_list.append(ev.average_score)
		highest_year = max(year_list)
		lowest_year = min(year_list)
		highest_battery_size = max(battery_size_list)
		lowest_battery_size = min(battery_size_list)
		highest_range = max(range_list)
		lowest_range = min(range_list)
		highest_cost = max(cost_list)
		lowest_cost = min(cost_list)
		highest_power = max(power_list)
		lowest_power = min(power_list)
		highest_average_score = max(average_score_list)
		lowest_average_score = min(average_score_list)
		template_values = {
			'url':url,
			'url_string':url_string,
			'user':user,
			'evs':evs,
			'highest_year':highest_year,
			'lowest_year':lowest_year,
			'highest_battery_size':highest_battery_size,
			'lowest_battery_size':lowest_battery_size,
			'highest_range':highest_range,
			'lowest_range':lowest_range,
			'highest_cost':highest_cost,
			'lowest_cost':lowest_cost,
			'highest_power':highest_power,
			'lowest_power':lowest_power,
			'highest_average_score':highest_average_score,
			'lowest_average_score':lowest_average_score,
		}
		template = JINJA_ENVIROMENT.get_template('compare-vehicles.html')
		self.response.write(template.render(template_values))

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
