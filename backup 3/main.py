from stocks import StockDB

stock_db = StockDB("data.db")
stock_db.init_db()

stock_db.update()