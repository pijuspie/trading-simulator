import os
from flask import Flask, send_from_directory, abort, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from stocks import StockManager
from users import UserManager

STATIC = "static"

app = Flask(__name__, static_folder=STATIC)
app.secret_key = "abra ka dabra"

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
        return "Internal server error", 500

    stockManager = StockManager() 
    stocks = stockManager.getStocks()

    stock = None
    for s in stocks:
        if s.getTicker() == ticker:
            stock = s

    if stock is None:
        return "Stock not found", 404

    prices = stockManager.getPrices(stock.getId(), interval)
    stockManager.closeDB()

    jsonObject = {"ticker": stock.getTicker(), "name": stock.getName(), "prices": []}
    for p in prices:
        jsonObject["prices"].append({"timestamp": p.getTimestamp(), "price": round(p.getPrice(), 2)})

    return jsonify(jsonObject)

@app.post("/api/login")
def post_login():
    credentials = request.get_json()
    username = credentials["username"]
    password = credentials["password"]

    userManager = UserManager() 
    user = userManager.getUser(username)
    if user is None:
        return "User not found", 401

    if not check_password_hash(user.getPasswordHash(), password):
        return "Incorrect password", 401

    session["userId"] = user.getId()
    return "Successfully logged in", 200

@app.post("/api/signup")
def post_signup():
    credentials = request.get_json()
    username = credentials["username"]
    email = credentials["email"]
    password = credentials["password"]

    userManager = UserManager() 
    if userManager.checkIfUserExists(username, email):
        return "Username or email already exists", 409

    passwordHash = generate_password_hash(password)
    userManager.addUser(username, email, passwordHash)
    user = userManager.getUser(username)
    if user is None:
        return "Internal server error", 500

    session["userId"] = user.getId()
    return "Successfully signed up", 200      

@app.get("/api/logout")
def post_logout():
    session.pop("userId", None)
    return "Successfully logged out", 200      

@app.route("/")
def home():
    return send_from_directory(STATIC, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    fullPath = os.path.join(STATIC, path)
    if os.path.isfile(fullPath):
        return send_from_directory(STATIC, path)

    indexPath = os.path.join(fullPath, "index.html")
    if os.path.isfile(indexPath):
        return send_from_directory(os.path.join(STATIC, path), "index.html")

    abort(404)