from Database import MongoTools
import csv
import datetime

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
			user = walden.find_from_email(row[0])
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