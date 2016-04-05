import MongoTools as mTools
from Routing import WorkWave as ww

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
            print "adding..." + walden_ID,
            local.add_from_walden_record(user)

        print "Done!"

    print "Done updating from Walden"
    local.disconnect()
    walden.disconnect()

def update_local_from_WW():
    # as of now this doesn't remove ones that have been flag as no longer delivering
    # even though they have been deleted from WW
    print "Getting orders from WW...",
    # Get order list from WW
    response = ww.get_orders()
    print "Done"

    # Check Error Codes
    if (response.status_code != 200):
        return False

    # Get actual order data
    orders = response.json()['orders']

    # Get Local DB
    local = mTools.LocalDB()

    print "Cycling through orders...",
    for order in orders:
        ww_order = orders[order]
        walden_ID = ww_order['delivery']['customFields']['walden_ID']
        local.set_ww_ID(walden_ID, ww_order['id'])
    print "Done"

    local.disconnect()
    return True


def update_local_mid_month():
    # First update from ww
    flag = update_local_from_WW()
    if not flag:
        print "Update from WW not successfull"
        return False

    # Get WaldenDB
    print "Updating from Walden...",
    update_local_from_walden()
    print "Done"


    local = mTools.LocalDB()
    # Build add/drop arrays
    drop_IDs = []
    add_array = []
    all_orders = local.get_all()
    for order in all_orders:
        if order['status'] == "active":
            if 'workwave_ID' not in order:
                add_array.append( ww.build_order_from_document(order) )
        else:
            if 'workwave_ID' in order:
                drop_IDs.append( order['workwave_ID'] )

    local.disconnect()

    print "num to drop: " + str(len(drop_IDs))
    print "num to add: " + str(len(add_array))

    # Send to work wave
    response = ww.add_orders(add_array)
    print "added: " + str(response.status_code)
    response = ww.drop_orders(drop_IDs)
    print "deleted: " + str(response.status_code) + "  " + response.text
