import MongoTools as mTools

# Initialize database
MONGO_DB_LOCATION = 'mongodb://localhost:27017/'
DB_PATH = 'test_database'
ORDERS_COLLECTION = 'orders'
db = mTools.Collection(MONGO_DB_LOCATION, DB_PATH, ORDERS_COLLECTION)


def add_entry(entry_dic):
	print("build me")
	
def len():
	return 1

def delete_orders():
	print "build me"