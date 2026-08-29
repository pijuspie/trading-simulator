from stocks import initializeStockManager
from users import initializeUserManager
from database import Database

db = Database("database.db")
stockManager = initializeStockManager(db)
userManager = initializeUserManager(db)

stockManager.updatePrices()