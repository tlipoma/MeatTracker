from pymongo import MongoClient

class Collection:
	client = None
	current_db = None
	current_collection = None

	def __init__(self, location, db, collection):
		# TODO: Add error checking to all this
		# TODO: Add ability to use user/pass
		self.client = MongoClient(location)
		self.current_db = self.client[db]
		self.current_collection = self.current_db[collection]