import dataset

class DataSET:

    db = None

    def __init__(self, db_address):
        self.db = dataset.connect(db_address)
