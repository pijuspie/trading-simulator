class UserDB:
    def __init__(self, db):
        self.db = db
        self.connection = db.connection
        self.cursor = db.cursor

    



