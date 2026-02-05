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

project_db = None

def init_project_db(path):
    global project_db
    project_db = ProjectDB(path)

class ProjectDB:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def init_db(self):
        self.cursor.execute("CREATE TABLE user_list (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL);")
        self.cursor.execute("CREATE TABLE project_list (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);")
        self.cursor.execute("CREATE TABLE project_members (user_id INTEGER NOT NULL, project_id INTEGER NOT NULL, PRIMARY KEY (user_id, project_id));")
        self.cursor.execute("CREATE TABLE certificates (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, project_id INTEGER NOT NULL, stock_id TEXT NOT NULL, shares REAL NOT NULL, init_value REAL NOT NULL, timestamp INTEGER NOT NULL);")
        self.connection.commit()
        print("ProjectDB initialised")

    def insert_user(self, name, email, password):
        self.cursor.execute(f"INSERT INTO user_list (name, email, password) VALUES ('{name}', '{email}', '{password}');")
        self.connection.commit()

    def select_user_by_credentials(self, name, password):
        self.cursor.execute(f"SELECT * FROM user_list WHERE name='{name}' AND password='{password}';")
        return self.cursor.fetchone()

    def select_user_by_id(self, id):
        self.cursor.execute(f"SELECT * FROM user_list WHERE id='{id}';")
        return self.cursor.fetchone()

    def delete_user(self, id):
        self.cursor.execute(f"DELETE FROM user_list WHERE id='{id}';")
        self.connection.commit()

    def insert_project(self, name):
        self.cursor.execute(f"INSERT INTO project_list (name) VALUES ('{name}');")
        self.connection.commit()

    def select_project(self, id):
        self.cursor.execute(f"SELECT * FROM project_list WHERE id='{id}';")
        return self.cursor.fetchone()

    def delete_project(self, id):
        self.cursor.execute(f"DELETE FROM project_list WHERE id='{id}';")
        self.connection.commit()

    def insert_user_to_project(self, user_id, project_id):
        self.cursor.execute(f"INSERT INTO project_members (user_id, project_id) VALUES ('{user_id}', '{project_id}');")
        self.connection.commit()
    
    def select_users_in_project(self, project_id):
        self.cursor.execute(f"SELECT user_id FROM project_members WHERE project_id='{project_id}';")
        return self.cursor.fetchall()

    def select_projects_in_user(self, user_id):
        self.cursor.execute(f"SELECT project_id FROM project_members WHERE user_id='{user_id}';")
        return self.cursor.fetchall()

    def delete_user_from_project(self, user_id, project_id):
        self.cursor.execute(f"DELETE FROM project_members WHERE user_id='{user_id}' AND project_id='{project_id}';")
        self.connection.commit()
    
    def insert_certificate(self, user_id, project_id, stock_id, shares, init_value, timestamp):
        self.cursor.execute(f"INSERT INTO certificates (user_id, project_id, stock_id, shares, init_value, timestamp) VALUES ('{user_id}', '{project_id}', '{stock_id}', '{shares}', '{init_value}', '{timestamp}');")
        self.connection.commit()

    def select_certificates_in_project(self, project_id):
        self.cursor.execute(f"SELECT * FROM certificates WHERE project_id='{project_id}';")
        return self.cursor.fetchall()