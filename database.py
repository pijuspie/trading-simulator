import sqlite3

class Database:
    def __init__(self, path: str):
        self.path = path
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()

    def commit(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()
    
    def fetchone(self, sql: str) -> tuple[str | int | float, ...] | None:
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def fetchall(self, sql: str) -> list[tuple[str | int | float, ...]]:
        self.cursor.execute(sql)
        return self.cursor.fetchall()