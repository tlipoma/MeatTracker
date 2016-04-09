from Database import MongoTools
from Database import DBTools
from Routing import WorkWave
import json
import csv
import datetime

def build_route_csv(day):
	print "Getting routes"
	# get routes from WW
	routes_response = WorkWave.get_routes_on_day(day)
	if routes_response.status_code != 200:
		print routes_response.text
		return None
	routes = routes_response.json()['routes']

	print "Getting DBs"
	# Get Databases
	local = MongoTools.LocalDB()
	walden = MongoTools.WaldenDB()

	deliveries = {}
	for route in routes:
		this_route = routes[route]
		# build section
		steps = this_route['steps']
		lines = []
		for step in steps:
			line = {}
			if "orderId" in step:
				delivery = local.get_delivery_by_WW_id(step['orderId'])
				walden_order = walden.find_from_ID(delivery['walden_ID'])

				line['walden_ID'] = delivery['walden_ID']
				line['delivery_time'] = get_time_from_sec(step['arrivalSec'])
				line['name'] = delivery['name_first'] + " " + delivery['name_last']
				line['address_1'] = delivery['address_1']
				line['address_2'] = delivery['address_2']
				line['city'] = delivery['city']
				line['zip_code'] = delivery['zip_code']
				
				line['phone'] = walden_order['phone']
				note = ""
				if 'location_type' in delivery:
					note += delivery['location_type']
				note += ' - '
				if 'notes' in walden_order:
					if walden_order['notes'] != None:
						note += walden_order['notes']
				line['note'] = note

				lines.append(line)
		deliveries[WorkWave.get_truck_name(this_route['vehicleId'])] = lines

	local.disconnect()
	walden.disconnect()

	#Convert to csv
	print "Converting to csv..."
	csv_array = []
	for truck in deliveries:
		csv_array.append("\n\n\n" +truck + "\n")
		route = deliveries[truck]
		for stop in route:
			line = "" + ','
			line += "" + ','
			line += stop['delivery_time'] + ","
			line += stop['name'] + ","
			line += "" + ','
			line += "" + ','
			line += "" + ','
			line += "" + ','
			line += "" + ','
			line += "" + ','
			line += stop['address_1']
			if stop['address_2'] != None:
				line += " - " + stop['address_2'] + ","
			else:
				line += " - " + ","
			line += stop['city'] + ","
			line += stop['zip_code'] + ","
			line += stop['phone'] + ","
			line += "" + ','
			line += "" + ','
			line += "" + ','
			line += "" + ','
			line += stop['walden_ID'] + ","
			csv_array.append(line + "\n")
	return csv_array

def get_time_from_sec(sec):
	h = sec/60.0/60.0
	hour = int(h)
	minute = int((h-hour)*60)
	return str(hour) + ":" + str(minute)

def update_mid_month():
	DBTools.update_local_mid_month()

def update_ww_id_from_WW():
	DBTools.update_local_from_WW()

def init_DB_from_WW():
	DBTools.init_local_from_WW()

def send_all_orders_to_WW():
	# this adds all active deliveries to WW
	# Make sure to clear WW before doing this
	local = MongoTools.LocalDB()

	print "Building deliveries array"
	deliveries = local.get_all_active_deliveries()

	order_array = []
	for order in deliveries:
		order_array.append(WorkWave.build_order_from_document(order))

	# Calulate time to add and send
	time = len(order_array)/60.0 # len of time to add in minutes
	print "Sending to WorkWave - this should take " + str(time) + " minutes"
	response = WorkWave.add_orders(order_array)
	print response
	print response.text

	local.disconnect()

def send_order_to_WW(orderID):
	local = MongoTools.LocalDB()
	order = local.get_delivery_by_walden_id(orderID)
	ordersArray = [WorkWave.build_order_from_document(order)]
	response = WorkWave.add_orders(ordersArray)
	print response
	print response.text
	local.disconnect()
	return response

def set_order_date_to_WW(orderID, set_date):
	local = MongoTools.LocalDB()
	local_order = local.get_delivery_by_walden_id(orderID)
	order = WorkWave.build_order_from_document(local_order, startDate=set_date, lockDate=True)

	# Send to WW
	response = WorkWave.replace_order(order, local_order['workwave_ID'])
	print response.text
	local.disconnect()
	return response


def update_DB_from_walden():
	DBTools.update_local_from_walden()

def init_DB_from_LastDelivery(location_to_csv):

	# Get CSV
	with open(location_to_csv, 'r') as csvfile:
		# Init Databases
		walden = MongoTools.WaldenDB()
		local = MongoTools.LocalDB()

		# Clear Local DB first
		local.delete_all_local_documents()

		users_not_found = []

		# Cycle through csv
		dateReader = csv.reader(csvfile, delimiter=',')
		for row in dateReader:
			print("adding: " + row[0])
			new_doc = {}
			# Convert time to datetime and back for consistancy
			try:
				date = datetime.datetime.strptime(row[1], "%m/%d/%Y")
				date = date.strftime("%m/%d/%Y")
			except:
				print("couldn't convert time")
				date = ""
			# Get user from walden DB
			#user = walden.find_from_email(row[0])
			user = walden.find_from_ID(row[0])
			if (user != None):
				# build new doc
				new_doc['walden_ID'] = user['_id']
				new_doc['email'] = user['email']
				new_doc['last_delivery_date'] = date
				# Save to local db
				local.add_delivery(new_doc)
			else:
				print("Could not find matching user for " + row[0])
				users_not_found.append(row[0])

		# Close the databases
		walden.disconnect()
		local.disconnect()

		print("Done! List of users we couldn't match: ")
		for user in users_not_found:
			print user