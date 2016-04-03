import datetime
from calendar import monthrange
import os
import requests
import json

WORK_WAVE_KEY = os.environ['WORK_WAVE_API_KEY']
WORK_WAVE_BASE_URL = "https://wwrm.workwave.com/api/v1/"
WORK_WAVE_PRIMARY_TERRITORY = "2eafce5c-e559-4b09-8a9f-3181f20bf726"

DELIVERY_DATE_DELTA = 2 # add +- days to last delivery date for new window
DEFAULT_SERVICE_TIME = 180 # 3 minutes in seconds

def get_from_WW(urlExtension):
    url = WORK_WAVE_BASE_URL + urlExtension
    headers = {}
    headers['X-WorkWave-Key'] = WORK_WAVE_KEY
    return requests.get(url, headers=headers)

def post_to_WW(urlExtension, postdata):
    url = WORK_WAVE_BASE_URL + urlExtension
    headers = {}
    headers['X-WorkWave-Key'] = WORK_WAVE_KEY
    headers['Content-Type'] = "application/json"
    return requests.post(url, data=json.dumps(postdata), headers=headers)

def add_orders(orderArray):
    data = {}
    data['orders'] = orderArray
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/orders"
    return post_to_WW(urlExtension, data)

def get_orders():
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/orders"
    return get_from_WW(urlExtension)

def get_territories():
    return get_from_WW("territories")

def build_order_from_document(inD):
    order = {}

    # name
    full_name = inD['name_first'] + " " + inD['name_last']
    order['name'] = full_name
    
    # eligibility
    # get last delivery date
    eligibility = {}
    last_date = inD['last_delivery_date']
    if (last_date == 0):
        eligibility['type'] = "any"
    else:
        today = datetime.datetime.today()
        last_date = datetime.datetime.strptime(inD['last_delivery_date'], "%m/%d/%Y")
        # if last day was more than a month ago, reset to any
        if (today-last_date).days > 32:
            eligibility['type'] = "any"
        else:
            this_date = last_date + datetime.timedelta(days=monthrange(last_date.year, last_date.month)[1])
            eligibility['type'] = "on"
            date_array = []
            # Go back num of days, then add in delivery dates
            this_date = this_date - datetime.timedelta(days=DELIVERY_DATE_DELTA)
            for i in range((DELIVERY_DATE_DELTA*2) +1):
                date_array.append(this_date.strftime("%Y%m%d"))
                this_date = this_date + datetime.timedelta(days=1)
            eligibility['onDates'] = date_array
    order['eligibility'] = eligibility

    # Address
    location = {}
    address_string = inD['address_1'] + ", " + inD['city'] + ", " + inD['state'] + " " + inD['zip_code'] + ", " + "USA"
    location['address'] = address_string

    # Delivery Time
    timeWindows = []
    window = {}
    if inD['location_type'] == 'buisness':
        window['startSec'] = 32400 # 9am in seconds
        window['endSec'] = 61200   # 5pm in seconds
    else:
        window['startSec'] = 28800 # 8am in seconds
        window['endSec'] = 68400   # 7pm in seconds
    timeWindows.append(window)

    # build delivery
    delivery = {}
    delivery['depotId'] = None
    delivery['notes'] = "no notes"
    delivery['tagsIn'] = []
    delivery['tagsOut'] = []
    delivery['location'] = location
    delivery['timeWindows'] = timeWindows
    delivery['serviceTimeSec'] = DEFAULT_SERVICE_TIME
    customFields = {}
    customFields['walden_ID'] = inD['walden_ID']
    delivery['customFields'] = customFields
    order['delivery'] = delivery

    # random
    order['priority'] = 0
    order['loads'] = {}
    order['forceVehicleId'] = None
    order['pickup'] = None
    order['isService'] = True
    # No notes yet
    
    return order
