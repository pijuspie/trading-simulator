from stocks import StockDB

stock_db = StockDB("data.db")
stock_db.update()
print(stock_db.get_stock_prices_all())
