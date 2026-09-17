import database
import stocks
from app import app
import threading
import time

database.initialize()
stocks.initialize()

def updater():
    while True:
        stockManager = stocks.StockManager()
        stockManager.updatePrices()
        stockManager.closeDB()
        time.sleep(60)

threading.Thread(target=updater, daemon=True).start()

app.run()