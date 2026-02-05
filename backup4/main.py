from stocks import init_stock_db, stock_db
from project import init_project_db, project_db
from app import app

init_stock_db("stocks.db")
init_project_db("project.db")
app.run(debug=True)

# stock_db.init_db()
# stock_db.update()
# project_db.init_db()
