from database import Database
from datetime import datetime

class User:
    def __init__(self, id: int, name: str, email: str, passwordHash: str):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__passwordHash = passwordHash

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getEmail(self):
        return self.__email

    def getPasswordHash(self):
        return self.__passwordHash

class Project:
    def __init__(self, id: int, name: str, initialBalance: float, balance: float):
        self.__id = id
        self.__name = name
        self.__initialBalance = initialBalance
        self.__balance = balance

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getInitialBalance(self):
        return self.__initialBalance

    def getBalance(self):
        return self.__balance
    
class StockCertificate:
    def __init__(self, id: int, userId: int, projectId: int, stockId: int, quantity: float, purchasePrice: float, purchaseTimestamp: int, status: str):
        self.__id = id
        self.__userId = userId
        self.__projectId = projectId
        self.__stockId = stockId
        self.__quantity = quantity
        self.__purchasePrice = purchasePrice
        self.__purchaseTimestamp = purchaseTimestamp
        self.__status = status

    def getId(self):
        return self.__id

    def getUserId(self):
        return self.__userId
    
    def getProjectId(self):
        return self.__projectId
    
    def getStockId(self):
        return self.__stockId
    
    def getQuantity(self):
        return self.__quantity
    
    def getPurchasePrice(self):
        return self.__purchasePrice
    
    def getPurchaseTimestamp(self):
        return self.__purchaseTimestamp
    
    def getStatus(self):
        return self.__status    

class UserManager:
    def __init__(self):
        self.__db = Database()

    def addUser(self, name: str, email: str, passwordHash: str):
        self.__db.cursor.execute("INSERT INTO User (username, email, passwordHash) VALUES (?, ?, ?);", (name, email, passwordHash))
        self.__db.connection.commit()

    def getUser(self, name: str):
        self.__db.cursor.execute("SELECT userId, username, email, passwordHash FROM User WHERE username = ?;", (name,))
        user = self.__db.cursor.fetchone()
        if user is None:
            return None
        return User(int(user[0]), str(user[1]), str(user[2]), str(user[3]))

    def checkIfUserExists(self, name: str, email: str):
        self.__db.cursor.execute("SELECT userId FROM User WHERE username = ? OR email = ?;", (name, email))
        users = self.__db.cursor.fetchall()
        return len(users) > 0

    def getUserById(self, id: int):
        self.__db.cursor.execute("SELECT userId, username, email, passwordHash FROM User WHERE userId = ?;", (id,))
        user = self.__db.cursor.fetchone()
        return User(int(user[0]), str(user[1]), str(user[2]), str(user[3]))

    def removeUser(self, id: int):
        self.__db.cursor.execute("DELETE FROM User WHERE userId = ?;", (id,))
        self.__db.connection.commit()

    def getProject(self, id: int):
        self.__db.cursor.execute("SELECT projectId, projectName, initialBalance, balance FROM Project WHERE projectId = ?;", (id,))
        project = self.__db.cursor.fetchone()
        if project is None:
            return None
        return Project(int(project[0]), str(project[1]), float(project[2]), float(project[3]))

    def getProjectByName(self, name: str):
        self.__db.cursor.execute("SELECT projectId, projectName, initialBalance, balance FROM Project WHERE projectName = ?;", (name,))
        project = self.__db.cursor.fetchone()
        return Project(int(project[0]), str(project[1]), float(project[2]), float(project[3]))

    def addProject(self, name: str, initBalance: float):
        self.__db.cursor.execute("INSERT INTO Project (projectName, initialBalance, balance) VALUES (?, ?, ?);", (name, initBalance, initBalance))
        self.__db.connection.commit()

    def removeProject(self, id: int):
        self.__db.cursor.execute("DELETE FROM Project WHERE projectId = ?;", (id,))
        self.__db.connection.commit()

    def addUserProject(self, userId: int, projectId: int):
        self.__db.cursor.execute("INSERT INTO UserProject (userId, projectId) VALUES (?, ?);", (userId, projectId))
        self.__db.connection.commit()

    def checkIfUserInProject(self, userId: int, projectId: int):
        self.__db.cursor.execute("SELECT userId FROM UserProject WHERE projectId = ? AND userId = ?;", (projectId, userId))
        user = self.__db.cursor.fetchone()
        return user is not None

    def getUsers(self, projectId: int):
        self.__db.cursor.execute("SELECT userId FROM UserProject WHERE projectId = ?;", (projectId,))
        users = self.__db.cursor.fetchall()
        return [int(user[0]) for user in users]

    def getProjects(self, userId: int):
        self.__db.cursor.execute("SELECT projectId FROM UserProject WHERE userId = ?;", (userId,))
        projects = self.__db.cursor.fetchall()
        return [int(project[0]) for project in projects]

    def removeUserProject(self, userId: int, projectId: int):
        self.__db.cursor.execute("DELETE FROM UserProject WHERE userId = ? AND projectId = ?;", (userId, projectId))
        self.__db.connection.commit()
    
    def openStockCertificate(self, userId: int, projectId: int, stockId: int, quantity: float, purchasePrice: float):
        purchaseTimestamp = int(datetime.now().timestamp())
        self.__db.cursor.execute("UPDATE Project SET balance = balance - ? WHERE projectId = ?;", (purchasePrice, projectId))
        self.__db.cursor.execute("INSERT INTO StockCertificate (userId, projectId, stockId, quantity, purchaseTimestamp, purchasePrice, certificateStatus) VALUES (?, ?, ?, ?, ?, ?, ?);", (userId, projectId, stockId, quantity, purchaseTimestamp, purchasePrice, "OPEN"))
        self.__db.connection.commit()

    def closeStockCertificate(self, certificateId: int, price: float):
        self.__db.cursor.execute("""
            UPDATE Project
            SET balance = balance + ?
            WHERE projectId = (
                SELECT projectId
                FROM StockCertificate
                WHERE certificateId = ?
            );
        """, (price, certificateId))
        self.__db.cursor.execute("UPDATE StockCertificate SET certificateStatus = ? WHERE certificateId = ?;", ("CLOSED", certificateId))
        self.__db.connection.commit()

    def getStockCertificates(self, projectId):
        self.__db.cursor.execute("SELECT certificateId, userId, projectId, stockId, quantity, purchasePrice, purchaseTimestamp, certificateStatus FROM StockCertificate WHERE projectId = ?;", (projectId,))
        certificates = self.__db.cursor.fetchall()
        return [StockCertificate(int(c[0]), int(c[1]), int(c[2]), int(c[3]), float(c[4]), float(c[5]), int(c[6]), str(c[7])) for c in certificates]

    def getStockCertificate(self, certificateId):
        self.__db.cursor.execute("SELECT certificateId, userId, projectId, stockId, quantity, purchasePrice, purchaseTimestamp, certificateStatus FROM StockCertificate WHERE certificateId = ?;", (certificateId,))
        c = self.__db.cursor.fetchone()
        if c is None:
            return None
        return StockCertificate(int(c[0]), int(c[1]), int(c[2]), int(c[3]), float(c[4]), float(c[5]), int(c[6]), str(c[7]))

    def closeDB(self):
        self.__db.close()