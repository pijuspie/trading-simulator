import os
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, abort, jsonify, request
from stocks import StockManager
from users import UserManager


STATIC = "static"

app = Flask(__name__, static_folder=STATIC)

@app.get("/api/stocks")
def get_stocks():
    stockManager = StockManager() 

    stocks = stockManager.getStocks()
    prices = [stockManager.getPriceNow(s.getId()).getPrice() for s in stocks]

    stockManager.closeDB()

    jsonObject = []
    for i in range(len(stocks)):
        s = stocks[i]
        jsonObject.append({"name": s.getName(), "ticker": s.getTicker(), "price": round(prices[i], 2), "change": round(float(0), 2)})

    return jsonify(jsonObject)

@app.get("/api/history")
def get_stock_history():
    ticker = request.args.get("ticker")
    interval = request.args.get("interval")
    if ticker is None or interval is None:
        abort(500)

    stockManager = StockManager() 
    stocks = stockManager.getStocks()

    stock = None
    for s in stocks:
        if s.getTicker() == ticker:
            stock = s

    if stock is None:
        abort(404)

    prices = stockManager.getPrices(stock.getId(), interval)
    stockManager.closeDB()

    jsonObject = {"ticker": stock.getTicker(), "name": stock.getName(), "prices": []}
    for p in prices:
        jsonObject["prices"].append({"timestamp": p.getTimestamp(), "price": round(p.getPrice(), 2)})

    return jsonify(jsonObject)

@app.route("/")
def home():
    return send_from_directory(STATIC, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    print(app.url_map)

    fullPath = os.path.join(STATIC, path)
    if os.path.isfile(fullPath):
        return send_from_directory(STATIC, path)

    indexPath = os.path.join(fullPath, "index.html")
    if os.path.isfile(indexPath):
        return send_from_directory(os.path.join(STATIC, path), "index.html")

    abort(404)