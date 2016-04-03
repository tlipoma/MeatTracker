from pymongo import MongoClient
import os

# Initialize database Variables
LOCAL_DB_NAME = 'MeatTracker'
LOCAL_COLLECTION = 'deliveries'
try:
    WALDEN_DB_LOCATION = os.environ['WALDEN_SERVER_LOCATION']
    WALDEN_DB_NAME = os.environ['WALDEN_DB_NAME']
    WALDEN_COLLECTION_NAME = os.environ['WALDEN_COLLECTION_NAME']
    LOCAL_DB_LOCATION = os.environ['LOCAL_SERVER_LOCATION']
except:
    print("oh no, cant find server locations in environment variables")



class WaldenDB:
    def __init__(self):
        self.client = MongoClient(WALDEN_DB_LOCATION)
        self.collection = self.client[WALDEN_DB_NAME][WALDEN_COLLECTION_NAME]
    def disconnect(self):
        self.client.close()

    # Functions for finding orders/deliveries/users
    def find_from_ID(self, id):
        return self.collection.find_one({'_id':str(id)})
    def find_from_email(self, email):
        return self.collection.find_one({'email':email})
    def get_all_users(self):
        return self.collection.find()


class LocalDB:
    def __init__(self):
        self.client = MongoClient(LOCAL_DB_LOCATION)
        self.collection = self.client[LOCAL_DB_NAME][LOCAL_COLLECTION]
    def disconnect(self):
        self.client.close()
    def delete_all_local_documents(self):
        self.collection.delete_many({})

    # Checking functions
    def id_exists(self, checkID):
        cursor = self.collection.find_one({'walden_ID':checkID})
        if (cursor == None):
            return False
        else:
            return True

    # Getting functions
    def get_delivery_by_walden_id(self, wid):
        return self.collection.find_one({'walden_ID': wid})
    def get_all_active_deliveries(self):
        return self.collection.find({'status': 'active'})


    # Adding functions
    def add_delivery(self, newDoc):
        self.collection.insert(newDoc)
    def add_from_walden_record(self, waldenDoccument):
        newDocument = create_document_from_walden_record(waldenDoccument)
        if newDocument != None:
            self.collection.insert_one(newDocument)
    def update_from_walden_record(self, waldenDoccument):
        updateDocument = update_document_from_walden_record(waldenDoccument)
        self.collection.update_one({'walden_ID':waldenDoccument['_id']}, {'$set': updateDocument})


def update_document_from_walden_record(waldenD):
    # Dont delete document if suspended or canceld
    # Delivery might already be in route
    # Wait until first month run to remove canceld orders
    newD = {}
    # ID and status
    newD['walden_ID'] = waldenD['_id']
    newD['status'] = waldenD['status']
    newD['name_first'] = waldenD['firstName']
    newD['name_last'] = waldenD['lastName']
    # Address items
    newD['address_1'] = waldenD['address']['address1']
    newD['address_2'] = waldenD['address']['address2']
    newD['city'] = waldenD['address']['city']
    newD['state'] = waldenD['address']['state']
    newD['zip_code'] = waldenD['address']['zipCode']
    newD['location_type'] = waldenD['deliveryType']

    return newD



def create_document_from_walden_record(waldenD):
    # Dont add if not active or if pickup type
    if (waldenD['status'] != 'active') or (waldenD['deliveryType'] == 'pickup'):
        return None

    newD = update_document_from_walden_record(waldenD)
    # Set blank delivery date
    newD['last_delivery_date'] = 0
    return newD