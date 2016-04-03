import MongoTools as mTools

# Use to update and find changes from main database into local
def update_local_from_walden():
	local = mTools.LocalDB()
	walden = mTools.WaldenDB()

	all_users = walden.get_all_users()
	num_orders = all_users.count()

	# Cycle through all the Walden Users
	cycle_number = 0
	for user in all_users:
		cycle_number += 1
		print "Checking order number " + str(cycle_number) + " out of " + str(num_orders),
		walden_ID = user['_id']

		# Check if it exits in local
		if local.id_exists(walden_ID):
			print "updating...",
			local.update_from_walden_record(user)
		else:
			print "adding...",
			local.add_from_walden_record(user)

		print "Done!"

	print "Done updating from Walden"
	local.disconnect()
	walden.disconnect()