from stocks import init_stock_db, get_stock_db
from datetime import datetime

init_stock_db("stocks.db")
stock_db = get_stock_db()
# stock_db.initializeDatabase()
stock_db.updatePrices()
