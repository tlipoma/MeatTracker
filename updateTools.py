from Database import DBTools as db
from Location import LocationTools as LocTools

def init_from_csv(file_location):
	# MAKE SURE NO ',' IN THE CSV!!!!

	# This will assume a blank Database!!!
	# Clear Database before using this!!!!

	# This assumes there is no header line

	# Assumes following colums
	# id, status, firstname, lastname, email, phone, stripe id
	# delivery type, address1, address2, city, state, zip,
	# shared loc, share size, portions, beef, pork, lamb, chicken, 
	# adventurous, eggs?, butter?, ground beef?, exclude, notes
	# delivery instructions, referrer, hold, prefs changes, -other stuff
	orderDic = {}
	fo = open(file_location, 'r')
	entryNumber = 0
	for line in fo:
		entryNumber += 1
		print "Adding entry " + str(entryNumber)
		order = {}
		orderArray = line.split(',')
		
		# Customer Info
		order['id'] = orderArray[0]
		order['status'] = orderArray[1]
		order['firstName'] = orderArray[2]
		order['lastname'] = orderArray[3]
		order['email'] = orderArray[4]
		order['phone'] = orderArray[5]

		# Address Info
		order['type'] = orderArray[7]
		order['address1'] = orderArray[8]
		order['address2'] = orderArray[9]
		order['city'] = orderArray[10]
		order['state'] = orderArray[11]
		order['zip'] = LocTools.fix_zipcode(orderArray[12])
		order['delivery_instructions'] = orderArray[26]
		addressString = order['address1'] + ',' + order['city'] + ',' + order['state'] + ',' + order['zip']
		lat, lng = LocTools.convert_address_to_latlng(addressString)
		order['lat'] = lat
		order['lng'] = lng
		#order[''] = orderArray[]

		# Meat Tracker Varabiles
		order['delivered_flag'] = False
		order['notes'] = orderArray[25]
		order['hold'] = orderArray[28]
		#order['estimated_delivery_date'] = ???

		# Add to Database
		db.add_entry(order)

	fo.close()

