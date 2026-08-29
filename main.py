from stocks import init_stock_manager, get_stock_manager
from users import init_user_manager, get_user_manager

init_stock_manager("database.db")
stock_manager = get_stock_manager()
# stock_manager.initializeDatabase()
# stock_manager.updatePrices()

init_user_manager("database.db")
user_manager = get_user_manager()
# user_manager.initializeDatabase()


