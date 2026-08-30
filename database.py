import sqlite3

PATH = "database.db"

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(PATH)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

def initialize():
    db = Database()

    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Stock (
            stockId INTEGER PRIMARY KEY AUTOINCREMENT,
            stockTicker TEXT NOT NULL UNIQUE,
            stockName TEXT NOT NULL UNIQUE
        );
    """)

    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockPrice (
            stockId INTEGER NOT NULL,
            price REAL NOT NULL, timestamp INTEGER NOT NULL,
            PRIMARY KEY (stockId, timestamp),
            CONSTRAINT fk_stockId FOREIGN KEY (stockId) REFERENCES Stock(stockId)
        );
    """)  

    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            userId INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            passwordHash TEXT NOT NULL
        );
    """)
    
    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Project (
            projectId INTEGER PRIMARY KEY AUTOINCREMENT,
            projectName TEXT NOT NULL UNIQUE,
            initialBalance REAL NOT NULL,
            balance REAL NOT NULL
        );
    """)
    
    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserProject (
            userId INTEGER NOT NULL,
            projectId INTEGER NOT NULL,
            PRIMARY KEY (userId, projectId),
            CONSTRAINT fk_userId FOREIGN KEY (userId) REFERENCES User(userId),
            CONSTRAINT fk_projectId FOREIGN KEY (projectId) REFERENCES Project(projectId)
        );
    """)
    
    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockCertificate (
            certificateId INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            projectId INTEGER NOT NULL,
            stockId INTEGER NOT NULL,
            quantity REAL NOT NULL,
            purchaseTimestamp INTEGER NOT NULL,
            purchasePrice REAL NOT NULL,
            certificateStatus TEXT NOT NULL,
            CONSTRAINT fk_userId FOREIGN KEY (userId) REFERENCES User(userId),
            CONSTRAINT fk_projectId FOREIGN KEY (projectId) REFERENCES Project(projectId),
            CONSTRAINT fk_stockId FOREIGN KEY (stockId) REFERENCES Stock(stockId)
        );
    """)

    db.connection.commit()
    db.close()