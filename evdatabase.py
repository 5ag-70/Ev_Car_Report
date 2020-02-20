from google.appengine.ext import ndb

class EvDatabase(ndb.Model):
	name = ndb.StringProperty(required=True)
	manufacturer = ndb.StringProperty(required=True)
	year = ndb.IntegerProperty(required=True)
	battery_size = ndb.IntegerProperty(required=True)
	range = ndb.IntegerProperty(required=True)
	cost = ndb.IntegerProperty(required=True)
	power = ndb.IntegerProperty(required=True)
	created_by = ndb.UserProperty()
	average_score = ndb.FloatProperty()
	carkey = ndb.StringProperty()
	date = ndb.DateTimeProperty()

class Review(ndb.Model):
	created_by = ndb.UserProperty()
	review = ndb.StringProperty()
	rating = ndb.IntegerProperty()
	date = ndb.DateTimeProperty()
	carkey = ndb.StringProperty()
