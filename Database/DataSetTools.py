import dataset

class DataSET:
    # TODO: fix errors with odd unicode characters entering to dabase

    db = None
    table = None

    def __init__(self, db_address, table_address):
        self.db = dataset.connect(db_address)
        self.table = self.db[table_address]

    def add_entry(self, entry_dic):
        try:
            self.table.insert(entry_dic)
            self.db.commit()
        except:
            print "there was an error commiting to db"
            print entry_dic
            input("Press Enter to continue...")
            self.db.rollback()

    def get_size_of(self):
        # This is a costly itteration and should be avoided
        count = 0
        for item in self.table.all():
            count += 1
        return count

    def delete_table(self):
        self.table.drop()