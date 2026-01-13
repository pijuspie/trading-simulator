from database import database, stock_db, user_db

db = database.Database("data.db")
stocks = stock_db.StockDB(db)
users = user_db.UserDB(db)

print(stocks.getStockList())
stocks.update()

print(stocks.getStockPrices(1))