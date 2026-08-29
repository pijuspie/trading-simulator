import sqlite3

# insert user
# select user
# delete user
# modify user TODO

# insert project
# select project
# delete project
# modify project TODO

# insert project member
# select projects in user
# select users in project
# delete project member

# insert certificate
# select certificates in project
# delete certificate

user_manager = None

def init_user_manager(path):
    global user_manager
    user_manager = UserManager(path)

def get_user_manager():
    global user_manager
    return user_manager

class UserManager:
    def __init__(self, path):
        self.__path = path
        self.__connection = sqlite3.connect(path)
        self.__cursor = self.__connection.cursor()

    def __commit(self, sql):
        self.__cursor.execute(sql)
        self.__connection.commit()
    
    def __readOne(self, sql):
        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    def __readAll(self, sql):
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def insert_user(self, name, email, password):
        self.__cursor.execute(f"INSERT INTO user_list (name, email, password) VALUES ('{name}', '{email}', '{password}');")
        self.__connection.commit()

    def select_user_by_credentials(self, name, password):
        self.__cursor.execute(f"SELECT * FROM user_list WHERE name='{name}' AND password='{password}';")
        return self.__cursor.fetchone()

    def select_user_by_id(self, id):
        self.__cursor.execute(f"SELECT * FROM user_list WHERE id='{id}';")
        return self.__cursor.fetchone()

    def delete_user(self, id):
        self.__cursor.execute(f"DELETE FROM user_list WHERE id='{id}';")
        self.__connection.commit()

    def insert_project(self, name):
        self.__cursor.execute(f"INSERT INTO project_list (name) VALUES ('{name}');")
        self.__connection.commit()

    def select_project(self, id):
        self.__cursor.execute(f"SELECT * FROM project_list WHERE id='{id}';")
        return self.__cursor.fetchone()

    def delete_project(self, id):
        self.__cursor.execute(f"DELETE FROM project_list WHERE id='{id}';")
        self.__connection.commit()

    def insert_user_to_project(self, user_id, project_id):
        self.__cursor.execute(f"INSERT INTO project_members (user_id, project_id) VALUES ('{user_id}', '{project_id}');")
        self.__connection.commit()
    
    def select_users_in_project(self, project_id):
        self.__cursor.execute(f"SELECT user_id FROM project_members WHERE project_id='{project_id}';")
        return self.__cursor.fetchall()

    def select_projects_in_user(self, user_id):
        self.__cursor.execute(f"SELECT project_id FROM project_members WHERE user_id='{user_id}';")
        return self.__cursor.fetchall()

    def delete_user_from_project(self, user_id, project_id):
        self.__cursor.execute(f"DELETE FROM project_members WHERE user_id='{user_id}' AND project_id='{project_id}';")
        self.__connection.commit()
    
    def insert_certificate(self, user_id, project_id, stock_id, shares, init_value, timestamp):
        self.__cursor.execute(f"INSERT INTO certificates (user_id, project_id, stock_id, shares, init_value, timestamp) VALUES ('{user_id}', '{project_id}', '{stock_id}', '{shares}', '{init_value}', '{timestamp}');")
        self.__connection.commit()

    def select_certificates_in_project(self, project_id):
        self.__cursor.execute(f"SELECT * FROM certificates WHERE project_id='{project_id}';")
        return self.__cursor.fetchall()

    def initializeDatabase(self):
        self.__commit("""
            CREATE TABLE User (
                userId INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                passwordHash TEXT NOT NULL
            );
        """)

        self.__commit("""
            CREATE TABLE Project (
                projectId INTEGER PRIMARY KEY AUTOINCREMENT,
                projectName TEXT NOT NULL UNIQUE,
                initialBalance REAL NOT NULL,
                balance REAL NOT NULL
            );
        """)

        self.__commit("""
            CREATE TABLE UserProject (
                userId INTEGER NOT NULL,
                projectId INTEGER NOT NULL,
                PRIMARY KEY (userId, projectId),
                CONSTRAINT fk_userId FOREIGN KEY (userId) REFERENCES User(userId),
                CONSTRAINT fk_projectId FOREIGN KEY (projectId) REFERENCES Project(projectId)
            );
        """)

        self.__commit("""
            CREATE TABLE StockCertificate (
                certificateId INTEGER PRIMARY KEY AUTOINCREMENT,
                userId INTEGER NOT NULL,
                projectId INTEGER NOT NULL,
                stockId INTERGER NOT NULL,
                quantity REAL NOT NULL,
                purchaseTimestamp INTEGER NOT NULL,
                purchasePrice REAL NOT NULL,
                certificateStatus TEXT NOT NULL,
                CONSTRAINT fk_userId FOREIGN KEY (userId) REFERENCES User(userId),
                CONSTRAINT fk_projectId FOREIGN KEY (projectId) REFERENCES Project(projectId)
                CONSTRAINT fk_stockId FOREIGN KEY (stockId) REFERENCES Stock(stockId)
            );
        """)

        print("UserDB initialised")