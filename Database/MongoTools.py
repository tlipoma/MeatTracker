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
    def get_email_from_id(self, id):
        record = self.collection.find_one({'_id':str(id)})
        if record:
            return record['email']
        else:
            return record


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
        return self.collection.find({'$or': [ {'status': 'active'},{'status':'manual'} ] })
    def get_all(self):
        return self.collection.find()
    def get_delivery_by_WW_id(self, wwid):
        return self.collection.find_one( {'workwave_ID' : wwid} )

    # Setting functions
    def set_ww_ID(self, wid, wwid):
        self.collection.update_one( {'walden_ID':wid}, {'$set': {'workwave_ID':wwid}} )
    def set_last_delivery(self, wid, dateString):
        self.collection.update_one( {'walden_ID':wid}, {'$set': {'last_delivery_date':dateString}} )

    # Adding functions
    def add_delivery(self, newDoc):
        self.collection.insert(newDoc)
    def add_from_walden_record(self, waldenDoccument):
        newDocument = create_document_from_walden_record(waldenDoccument)
        if newDocument != None:
            self.collection.insert_one(newDocument)
    def add_from_WW_record(self, work_record):
        newDocument = create_from_WW_order(work_record)
        self.collection.insert_one(newDocument)
    def update_from_walden_record(self, waldenDoccument):
        updateDocument = update_document_from_walden_record(waldenDoccument)
        self.collection.update_one({'walden_ID':waldenDoccument['_id']}, {'$set': updateDocument})

    # Removeing functions
    def remove_ww_id(self, waldenID):
	self.collection.update( {'walden_ID':waldenID}, {'$unset': {"workwave_ID":""}} )

def create_from_WW_order(wwOrder):
    newD = {}
    newD['walden_ID'] = wwOrder['delivery']['customFields']['walden_ID']
    newD['last_delivery_date'] = wwOrder['delivery']['customFields']['last_delivery_date']
    return newD

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
    address = waldenD['address']
    newD['address_1'] = address['address1']
    if address['address2'] != None:
        newD['address_2'] = address['address2']
    newD['city'] = address['city']
    newD['state'] = address['state']
    newD['zip_code'] = address['zipCode']
    newD['location_type'] = waldenD['deliveryType']

    return newD



def create_document_from_walden_record(waldenD):
    # Dont add if not active or if pickup type
    if waldenD['status'] == 'manual' or waldenD['status'] == 'active':
        if waldenD['deliveryType'] == 'pickup':
            return None
        newD = update_document_from_walden_record(waldenD)
        # Set blank delivery date
        newD['last_delivery_date'] = 0
        return newD
    return None
    
