import DataSetTools as ds

# Initialize database
DB_PATH = 'sqlite:///orders.db'
CUSTOMER_TABLE = 'customer'
data_base = ds.DataSET(DB_PATH, CUSTOMER_TABLE)


def add_entry(entry_dic):
	data_base.add_entry(entry_dic)
	
def len():
	return data_base.get_size_of()

def delete_orders():
	data_base.delete_table()