from stocks import StockManager
from users import StockCertificate
from datetime import datetime, date, timedelta
from statistics import stdev
from math import sqrt

def calculateWeightedAverageReturn(certificates: list[StockCertificate]):
    if len(certificates) == 0:
        return 0

    stockManager = StockManager()
    totalProfit = 0
    totalInvestment = 0

    for c in certificates:
        totalInvestment += c.getPurchasePrice()
        if c.getStatus() == "CLOSED":
            totalProfit += c.getSalePrice()
        else:
            totalProfit += stockManager.getPriceNow(c.getStockId()).getPrice() * c.getQuantity()

    stockManager.closeDB()

    return round((totalProfit-totalInvestment)/totalInvestment*100, 2)

def calculateDailyPortfolioValue(certificates: list[StockCertificate]):
    stockManager = StockManager()
    value: dict[date, float] = {}

    for c in certificates:
        prices = stockManager.getPrices(c.getStockId(), "1year")
        for p in prices:
            after = p.getTimestamp() >= c.getPurchaseTimestamp()
            before = c.getStatus() == "OPEN" or p.getTimestamp() <= c.getSaleTimestamp()
            if not after or not before:
                continue
            day = datetime.fromtimestamp(p.getTimestamp()).date()
            if day not in value:
                value[day] = 0
            value[day] += p.getPrice() * c.getQuantity()

    stockManager.closeDB()

    valueTimestamps = []
    for d in value:
        timestamp = int(datetime.combine(d, datetime.min.time()).timestamp())
        valueTimestamps.append({"timestamp": timestamp, "value": round(value[d], 2)})

    return valueTimestamps

def calculateDailyReturns(certificates: list[StockCertificate]):
    stockManager = StockManager()
    value: dict[date, float] = {}
    cashFlow: dict[date, float] = {}

    for c in certificates:
        prices = stockManager.getPrices(c.getStockId(), "1year")
        purchaseDay = datetime.fromtimestamp(c.getPurchaseTimestamp()).date()
        if purchaseDay not in cashFlow:
            cashFlow[purchaseDay] = 0
        cashFlow[purchaseDay] += c.getPurchasePrice()

        saleDay = date.today() + timedelta(days=10)
        if c.getStatus() == "CLOSED":
            saleDay = datetime.fromtimestamp(c.getSaleTimestamp()).date()
            if saleDay not in cashFlow:
                cashFlow[saleDay] = 0
            cashFlow[saleDay] -= c.getSalePrice()

        for p in prices:
            day = datetime.fromtimestamp(p.getTimestamp()).date()
            after = day >= purchaseDay
            before = day < saleDay
            if not after or not before:
                continue
            if day not in value:
                value[day] = 0
            value[day] += p.getPrice() * c.getQuantity()

    stockManager.closeDB()

    valueTimestamps = []
    for d in sorted(value)[1:]:
        timestamp = int(datetime.combine(d, datetime.min.time()).timestamp())
        if d not in cashFlow:
            cashFlow[d] = 0
        valueTimestamps.append({"timestamp": timestamp, "value": value[d], "cashFlow": cashFlow[d]})

    returnTimestamps = []
    for i in range(len(valueTimestamps)):
        if i == 0:
            continue
        returns = valueTimestamps[i]["value"]/(valueTimestamps[i-1]["value"]+valueTimestamps[i]["cashFlow"])-1
        returnTimestamps.append({"timestamp": valueTimestamps[i]["timestamp"], "value": round(returns*100, 4)})
    
    return returnTimestamps

def calculateVolatility(certificates: list[StockCertificate]):
    dailyReturns = calculateDailyReturns(certificates)
    if len(dailyReturns) <= 1:
        return 0
    volatility = stdev([x["value"] for x in dailyReturns]) * sqrt(252)
    return round(volatility, 2)

def calculateSharpeRatio(certificates: list[StockCertificate]):
    dailyReturns = calculateDailyReturns(certificates)
    if len(dailyReturns) <= 1:
        return 0

    sum = 0
    for x in dailyReturns:
        sum += x["value"]

    standardDeviation = stdev([x["value"] for x in dailyReturns])
    if standardDeviation == 0:
        return 0
    sharpeRatio = sum / len(dailyReturns) / standardDeviation * sqrt(252)
    return round(sharpeRatio, 2)

def calculateDailyNetCash(certificates: list[StockCertificate]):
    netCashDiff: dict[date, float] = {}

    if len(certificates) == 0:
        return netCashDiff

    for c in certificates:
        purchaseDay = datetime.fromtimestamp(c.getPurchaseTimestamp()).date()
        if purchaseDay not in netCashDiff:
            netCashDiff[purchaseDay] = 0
        netCashDiff[purchaseDay] -= c.getPurchasePrice()
        if c.getStatus() == "OPEN":
            continue
        saleDay = datetime.fromtimestamp(c.getSaleTimestamp()).date()
        if saleDay not in netCashDiff:
            netCashDiff[saleDay] = 0
        netCashDiff[saleDay] += c.getSalePrice()

    netCash: dict[date, float] = {}

    start = min(netCashDiff)
    end = date.today()

    day = start
    netCashNow = 0

    while day <= end:
        if day in netCashDiff:
            netCashNow += netCashDiff[day]
        netCash[day] = netCashNow
        day += timedelta(days=1)

    netCashTimestamps = []
    for d in netCash:
        timestamp = int(datetime.combine(d, datetime.min.time()).timestamp())
        netCashTimestamps.append({"timestamp": timestamp, "value": round(netCash[d], 2)})

    return netCashTimestamps

def calculateHighestAndLowestReturnStocks(certificates: list[StockCertificate]):
    profit: dict[int, float] = {}
    investment: dict[int, float] = {}

    stockManager = StockManager()

    for c in certificates:
        if c.getStockId() not in investment or c.getStockId() not in profit:
            investment[c.getStockId()] = 0
            profit[c.getStockId()] = 0

        investment[c.getStockId()] += c.getPurchasePrice()
        if c.getStatus() == "CLOSED":
            profit[c.getStockId()] += c.getSalePrice()-c.getPurchasePrice()
        else:
            currentPrice = stockManager.getPriceNow(c.getStockId()).getPrice()*c.getQuantity()
            profit[c.getStockId()] += currentPrice-c.getPurchasePrice()

    highest = -1
    lowest = -1
    for i in profit:
        if highest == -1:
            highest = i
            lowest = i

        returnHighest = profit[highest]/investment[highest]
        returnLowest = profit[lowest]/investment[lowest]
        returnI = profit[i]/investment[i]

        if returnI > returnHighest:
            highest = i
        if returnI < returnLowest:
            lowest = i

    highestReturnStock = stockManager.getStock(highest)
    lowestReturnStock = stockManager.getStock(lowest)
    stockManager.closeDB()

    return highestReturnStock, lowestReturnStock

def analyzeCertificates(certificates: list[StockCertificate]):
    highestReturn, lowestReturn = calculateHighestAndLowestReturnStocks(certificates)

    result = {
        "dailyPortfolioValue": calculateDailyPortfolioValue(certificates),
        "dailyNetCash": calculateDailyNetCash(certificates),
        "weightedAverageReturn": calculateWeightedAverageReturn(certificates),
        "dailyReturns": calculateDailyReturns(certificates),
        "volatility": calculateVolatility(certificates),
        "highestReturnStock": "-",
        "lowestReturnStock": "-"
    }

    if highestReturn is not None:
        result["highestReturnStock"] = highestReturn.getName()
        
    if lowestReturn is not None:
        result["lowestReturnStock"] = lowestReturn.getName()

    return result