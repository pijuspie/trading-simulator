import os
from flask import Flask, send_from_directory, abort, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from stocks import StockManager
from users import UserManager
import analytics

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


@app.get("/api/stock")
def get_stock():
    ticker = request.args.get("ticker")
    if ticker is None:
        return "Internal server error", 500

    stockManager = StockManager() 

    stock = stockManager.getStockByTicker(ticker)
    if stock is None:
        stockManager.closeDB()
        return "Stock not found", 404

    price = stockManager.getPriceNow(stock.getId()).getPrice()
    stockManager.closeDB()

    jsonObject = {"name": stock.getName(), "ticker": stock.getTicker(), "price": round(price, 2)}
    return jsonify(jsonObject), 200

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
        stockManager.closeDB()
        return "Stock not found", 404

    prices = stockManager.getPrices(stock.getId(), interval)
    stockManager.closeDB()

    jsonObject = {"ticker": stock.getTicker(), "name": stock.getName(), "prices": []}
    for p in prices:
        jsonObject["prices"].append({"timestamp": p.getTimestamp(), "price": round(p.getPrice(), 2)})

    return jsonify(jsonObject)

@app.get("/api/status")
def get_status():
    userId = session.get("userId")
    return jsonify({ "loggedIn": userId is not None}), 200
    
@app.post("/api/login")
def post_login():
    credentials = request.get_json()
    username = credentials["username"]
    password = credentials["password"]

    userManager = UserManager() 
    user = userManager.getUser(username)
    userManager.closeDB()
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
        userManager.closeDB()
        return "Username or email already exists", 409

    passwordHash = generate_password_hash(password)
    userManager.addUser(username, email, passwordHash)
    user = userManager.getUser(username)
    userManager.closeDB()
    if user is None:
        return "Internal server error", 500

    session["userId"] = user.getId()
    return "Successfully signed up", 200      

@app.get("/api/logout")
def get_logout():
    session.pop("userId", None)
    return "Successfully logged out", 200      

@app.get("/api/profile")
def get_profile():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    userManager = UserManager()
    user = userManager.getUserById(id)
    userManager.closeDB()
    jsonObject = {"username": user.getName(), "email": user.getEmail() }
    return jsonify(jsonObject), 200      

@app.get("/api/projects")
def get_projects():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    userManager = UserManager()
    projectIds = userManager.getProjects(id)

    jsonObject = []
    for projectId in projectIds:
        project = userManager.getProject(projectId)

        if project is None:
            userManager.closeDB()
            return "Internal server error", 500

        members = len(userManager.getUsers(projectId))
        jsonObject.append({"name": project.getName(), "members": members, "id": projectId})

    userManager.closeDB()
    return jsonify(jsonObject), 200

@app.get("/api/project")
def get_project():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    projectId = request.args.get("id")
    if projectId is None:
        return "Internal server error", 500
    projectId = int(projectId)

    userManager = UserManager()
    project = userManager.getProject(projectId)
    if project is None:
        userManager.closeDB()
        return "Project not found", 404

    jsonObject = {"name": project.getName(), "balance": round(project.getBalance(), 2), "initialBalance": round(project.getInitialBalance(), 2), "certificates": [], "members": []}
    certificates = userManager.getStockCertificates(projectId)

    stockManager = StockManager()

    for c in certificates:
        if c.getStatus() == "CLOSED":
            continue

        stock = stockManager.getStock(c.getStockId())
        owner = userManager.getUserById(c.getUserId())

        if stock is None:
            stockManager.closeDB()
            userManager.closeDB()
            return "Internal server error", 500

        priceNow = stockManager.getPriceNow(c.getStockId())
        value = priceNow.getPrice() * c.getQuantity()
        change = (value/c.getPurchasePrice()-1)*100

        certificateObject = {"id": c.getId(), "ticker": stock.getTicker(), "name": stock.getName(), "owner": owner.getName(), "price": round(value, 2), "change": round(change, 2)}
        jsonObject["certificates"].append(certificateObject)

    stockManager.closeDB()

    users = userManager.getUsers(projectId)
    for u in users:
        user = userManager.getUserById(u)
        jsonObject["members"].append({"name": user.getName(), "id": user.getId()})

    userManager.closeDB()
    return jsonify(jsonObject), 200

@app.post("/api/newproject")
def post_new_project():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    credentials = request.get_json()
    name = credentials["name"]
    initialBalance = credentials["initialBalance"]

    if name is None or initialBalance is None:
        return "Internal server error", 500
    
    userManager = UserManager()
    user = userManager.getUserById(id)
    if user is None:
        userManager.closeDB()
        return "Internal server error", 500

    userManager.addProject(name, initialBalance)
    project = userManager.getProjectByName(name)
    userManager.addUserProject(id, project.getId())
    userManager.closeDB()

    return jsonify({"projectId": project.getId()}), 200  

@app.post("/api/buy")
def post_buy_stock():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    credentials = request.get_json()
    projectId = credentials["projectId"]
    ticker = credentials["ticker"]
    quantity = credentials["quantity"]

    if projectId is None or ticker is None or quantity is None:
        return "Internal server error", 500

    if projectId == "":
        return "Internal server error", 500
    projectId = int(projectId)

    if quantity == "":
        return "Invalid quantity", 409
    quantity = float(quantity)

    stockManager = StockManager()
    stock = stockManager.getStockByTicker(ticker)
    if stock is None:
        stockManager.closeDB()
        return "Stock not found", 404

    price = stockManager.getPriceNow(stock.getId()).getPrice()
    value = price * quantity
    stockManager.closeDB()

    userManager = UserManager()
    project = userManager.getProject(projectId)
    if project is None:
        userManager.closeDB()
        return "Internal server error", 500

    if project.getBalance() < value:
        userManager.closeDB()
        return "Not enough balance", 409

    userManager.openStockCertificate(id, int(projectId), stock.getId(), quantity, value)
    userManager.closeDB()

    return "Transaction successful", 200  

@app.post("/api/sell")
def post_sell_stock():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    credentials = request.get_json()
    certificateId = credentials["certificateId"]

    if certificateId is None or certificateId == "":
        return "Internal server error", 500
    certificateId = int(certificateId)

    userManager = UserManager()
    certificate = userManager.getStockCertificate(certificateId)

    if certificate is None:
        userManager.closeDB()
        return "Internal server error", 500

    if certificate.getStatus() == "CLOSED":
        userManager.closeDB()
        return "The certificate is closed", 403

    if certificate.getUserId() != id:
        userManager.closeDB()
        return "User is not the owner of the certificate", 403

    stockManager = StockManager()
    price = stockManager.getPriceNow(certificate.getStockId()).getPrice()
    value = price * certificate.getQuantity()
    stockManager.closeDB()

    userManager.closeStockCertificate(certificateId, value)
    userManager.closeDB()
    
    return "Transaction successful", 200  

@app.post("/api/addmember")
def post_add_member():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    credentials = request.get_json()
    userName = credentials["userName"]
    projectId = credentials["projectId"]

    userManager = UserManager()
    if not userManager.checkIfUserInProject(id, projectId):
        userManager.closeDB()
        return "User is not in the project", 403

    user = userManager.getUser(userName)
    if user is None:
        userManager.closeDB()
        return "User not found", 404

    userManager.addUserProject(user.getId(), projectId)
    userManager.closeDB()
    
    return "Member added successfully", 200  

@app.post("/api/removemember")
def post_remove_member():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    credentials = request.get_json()
    projectId = credentials["projectId"]

    userManager = UserManager()
    if not userManager.checkIfUserInProject(id, projectId):
        userManager.closeDB()
        return "User is not in the project", 403

    userManager.removeUserProject(id, projectId)

    members = userManager.getUsers(projectId)
    if len(members) == 0:
        userManager.removeProject(projectId)

    certificates = userManager.getStockCertificates(projectId)
    stockManager = StockManager()

    for c in certificates:
        if c.getStatus() == "CLOSED":
            continue
        price = stockManager.getPriceNow(c.getStockId()).getPrice()
        value = price * c.getQuantity()
        userManager.closeStockCertificate(c.getId(), value)

    stockManager.closeDB()
    userManager.closeDB()
    return "Member added successfully", 200  

@app.get("/api/member")
def get_member_statistics():
    id = session.get("userId")
    if id is None:
        return "Unauthorized", 401

    projectId = request.args.get("projectId")
    userId = request.args.get("userId")
    if projectId is None or userId is None:
        return "Internal server error", 500
    projectId = int(projectId)
    userId = int(userId)

    userManager = UserManager()
    if not userManager.checkIfUserInProject(id, projectId):
        userManager.closeDB()
        return "User is not in the project", 403

    user = userManager.getUserById(userId)

    if not userManager.checkIfUserInProject(userId, projectId):
        userManager.closeDB()
        return "User is not in the project", 403

    certificates = userManager.getStockCertificates(projectId)
    userManager.closeDB()

    certificates = [c for c in certificates if c.getUserId() == userId]

    openC = [c for c in certificates if c.getStatus() == "OPEN"]
    closedC = [c for c in certificates if c.getStatus() == "CLOSED"]

    jsonObject = {
        "name": user.getName(),
        "certificates": {
            "open": analytics.analyzeCertificates(openC),
            "closed": analytics.analyzeCertificates(closedC),
            "all": analytics.analyzeCertificates(certificates)
        }        
    }

    return jsonify(jsonObject), 200  

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