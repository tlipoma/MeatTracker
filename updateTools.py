from Database import DBTools as db


def init_from_csv(file_location):
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
	for line in fo:
		order = {}
		orderArray = line.split(',')
		
		# Customer Info
		order['id'] = orderArray[0]
		order['status'] = orderArray[1]
		order['firstName'] = orderArray[2]
		order['lastname'] = orderArray[3]
		order['email'] = orderArray[4]
		order['phone'] = orderArray[5]

		# Delivery Info
		order[''] = orderArray[]

	fo.close()

