from repository.repository import Repository
from repository.stocks import StocksRepository


rep = Repository("data.db")
stocks = StocksRepository(rep)

print(stocks.getStockList())
stocks.update()
print(stocks.getStockPrices(1))

