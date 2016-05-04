import datetime
from calendar import monthrange
import os
import requests
import json

WORK_WAVE_KEY = os.environ['WORK_WAVE_API_KEY']
WORK_WAVE_BASE_URL = "https://wwrm.workwave.com/api/v1/"
WORK_WAVE_PRIMARY_TERRITORY = "2eafce5c-e559-4b09-8a9f-3181f20bf726"

DELIVERY_DATE_DELTA = 2 # add +- days to last delivery date for new window
MIN_DAYS_FROM_NOW = 3 # new adds must be this number of days in the future to allow for packing
DEFAULT_SERVICE_TIME = 240 # 3 minutes in seconds
DEFAULT_BUSINESS_SERVICE_TIME = 300 # 5 min in seconds

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

def delete_to_WW(urlExtension):
    url = WORK_WAVE_BASE_URL + urlExtension
    headers = {}
    headers['X-WorkWave-Key'] = WORK_WAVE_KEY
    headers['Content-Type'] = "application/json"
    return requests.delete(url, headers=headers)

def add_orders(orderArray):
    data = {}
    data['orders'] = orderArray
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/orders"
    return post_to_WW(urlExtension, data)

def replace_order(order, wwid):
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/orders/" + wwid
    return post_to_WW(urlExtension, order)

def drop_orders(dropArray):
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/orders?ids="
    for i in range(len(dropArray)):
        urlExtension += dropArray[i] + ","
    return delete_to_WW(urlExtension)


def get_orders():
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/orders"
    return get_from_WW(urlExtension)

def get_territories():
    return get_from_WW("territories")

def build_order_from_document(inD, startDate=None, lockDate=False):
    order = {}

    # name
    full_name = inD['name_first'] + " " + inD['name_last']
    order['name'] = full_name
    
    # eligibility
    # get last delivery date
    eligibility = {}
    last_date = inD['last_delivery_date']
    today = datetime.datetime.today()
    eligibility_days = []
    if lockDate:
        eligibility_days = get_eligibility_array(startDate, singeDay=True)
    elif last_date == 0:
        eligibility_days = get_eligibility_array(today, True)
    else:
        last_date = datetime.datetime.strptime(inD['last_delivery_date'], "%m/%d/%Y")
        # if last day was more than a month ago, reset to any
        if (today-last_date).days > 32:
            eligibility_days = get_eligibility_array(today, True)
        else:
            if startDate != None:
                this_date = startDate
                eligibility_days = get_eligibility_array(this_date, True)
            else:
                this_date = last_date + datetime.timedelta(days=monthrange(last_date.year, last_date.month)[1])
                eligibility_days = get_eligibility_array(this_date)
    eligibility['type'] = 'on'
    eligibility['onDates'] = eligibility_days
    order['eligibility'] = eligibility

    # Address
    location = {}
    try:
        address_string = inD['address_1'] + ", " + inD['city'] + ", " + inD['state'] + " " + inD['zip_code'] + ", " + "USA"
    except:
        print "failed on order: " + inD['walden_ID']
        #address_string = ""
    location['address'] = address_string

    # Delivery Time
    timeWindows = []
    window = {}
    if inD['location_type'] == 'business':
        window['startSec'] = 32400 # 9am in seconds
        window['endSec'] = 57600   # 5pm in seconds
    else:
        window['startSec'] = 18000 # 8am in seconds
        window['endSec'] = 72000   # 7pm in seconds
    timeWindows.append(window)

    # build delivery
    delivery = {}
    delivery['depotId'] = None
    delivery['notes'] = "no notes"
    delivery['tagsIn'] = []
    delivery['tagsOut'] = []
    delivery['location'] = location
    delivery['timeWindows'] = timeWindows
    if inD['location_type'] == 'business':
        delivery['serviceTimeSec'] = DEFAULT_BUSINESS_SERVICE_TIME
    else:
        delivery['serviceTimeSec'] = DEFAULT_SERVICE_TIME
    customFields = {}
    customFields['walden_ID'] = inD['walden_ID']
    customFields['last_delivery_date'] = inD['last_delivery_date']
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


def get_eligibility_array(startDay, anyFlag=False, singeDay=False):
    out_array = []

    if singeDay:
        out_array.append(startDay.strftime("%Y%m%d"))
        return out_array

    start = startDay - datetime.timedelta(days=DELIVERY_DATE_DELTA)
    end = startDay + datetime.timedelta(days=DELIVERY_DATE_DELTA)

    if anyFlag:
        start = datetime.datetime.today() + datetime.timedelta(days=MIN_DAYS_FROM_NOW)
        end = datetime.datetime(start.year, start.month, monthrange(start.year, start.month)[1])

    numDays = (end-start).days
    while end >= start:
        # Skip weekdays
        if start.weekday() != 5 and start.weekday() != 6:
            out_array.append(start.strftime("%Y%m%d"))
        start += datetime.timedelta(days=1)
    
    return out_array

def get_routes_on_day(day):
    day_string = day.strftime("%Y%m%d")
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/approved/routes?date=" + day_string
    return get_from_WW(urlExtension)

def get_truck_name(truckID):
    urlExtension = "territories/" + WORK_WAVE_PRIMARY_TERRITORY + "/vehicles"
    response = get_from_WW(urlExtension)
    if response.status_code == 200:
        all_trucks = response.json()['vehicles']
        for truck in all_trucks:
            if all_trucks[truck]['id'] == truckID:
                return all_trucks[truck]['externalId']
    return "no name"
